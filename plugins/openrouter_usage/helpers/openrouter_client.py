"""Merge OpenRouter keys, credits, and per-key activity."""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date as date_cls, datetime, timezone
from typing import Any

from helpers.plugins import get_plugin_config
from helpers.secrets import get_secrets_manager
from usr.plugins.openrouter_usage.helpers.aliases import label_for_key, parse_aliases
from usr.plugins.openrouter_usage.helpers.cache import TtlCache
from usr.plugins.openrouter_usage.helpers.fetch import OpenRouterError, get_json, with_query
from usr.plugins.openrouter_usage.helpers.format import format_number, format_usd

API_BASE = "https://openrouter.ai/api/v1"
_OVERVIEW_CACHE: TtlCache[dict[str, Any]] = TtlCache()
_OVERVIEW_LOCK = threading.Lock()


def load_settings(agent=None) -> dict[str, Any]:
    config = get_plugin_config("openrouter_usage", agent=agent) or {}
    watched = config.get("watched_key_hashes") or []
    if not isinstance(watched, list):
        watched = []
    return {
        "watched_key_hashes": [str(item).strip().lower() for item in watched if str(item).strip()],
        "key_aliases": str(config.get("key_aliases") or ""),
        "refresh_interval_minutes": max(1, int(config.get("refresh_interval_minutes") or 5)),
        "default_view": str(config.get("default_view") or "simple"),
        "show_token_counts": bool(config.get("show_token_counts", True)),
    }


def management_key() -> str:
    return get_secrets_manager().load_secrets().get("OPENROUTER_MANAGEMENT_KEY", "").strip()


def _unwrap_list(payload: Any, *keys: str) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def _unwrap_dict(payload: Any, *keys: str) -> dict[str, Any]:
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, dict):
                return value
        if "total_credits" in payload or "total_usage" in payload:
            return payload
    return {}


def _record_usd(record: dict[str, Any]) -> float:
    for key in ("usage", "usage_usd", "cost", "total_cost", "spend"):
        value = record.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def _record_tokens(record: dict[str, Any], field: str) -> int:
    value = record.get(field)
    if isinstance(value, (int, float)):
        return int(value)
    usage = record.get("usage")
    if isinstance(usage, dict) and isinstance(usage.get(field), (int, float)):
        return int(usage[field])
    return 0


def _date_key(raw: str) -> str:
    """Return YYYY-MM-DD from an ISO date string."""
    if not raw:
        return ""
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        return raw[:10]
    if raw.endswith("Z"):
        raw = raw.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw).strftime("%Y-%m-%d")
    except ValueError:
        return raw[:10] if len(raw) >= 10 else ""


def _chart_label(raw: str) -> str:
    if not raw:
        return ""
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        try:
            month = int(raw[5:7])
            day = int(raw[8:10])
            return f"{month}/{day}"
        except ValueError:
            return raw[:10]
    return raw[:10]


def _empty_payload(empty_state: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "ok": False,
        "empty_state": empty_state,
        "message": "Add OPENROUTER_MANAGEMENT_KEY to Agent Zero Secrets.",
        "credits": None,
        "keys": [],
        "totals": {},
        "summary": {},
        "daily": [],
        "models": [],
        "top_models": [],
        "providers": [],
        "top_providers": [],
        "per_key": [],
        "top_keys": [],
        "as_of": now,
        "last_error": None,
    }


def _fetch_credits(api_key: str) -> dict[str, Any]:
    return _unwrap_dict(get_json(f"{API_BASE}/credits", api_key), "data")


def _fetch_keys_list(api_key: str) -> list[Any]:
    return _unwrap_list(get_json(f"{API_BASE}/keys", api_key), "data", "keys")


def _fetch_key_activity(row: dict[str, Any], api_key: str) -> tuple[list[Any], str | None]:
    hash_value = str(row.get("hash") or row.get("hash_prefix") or "")
    if not hash_value:
        return [], None
    prefix = str(row.get("hash_prefix") or hash_value[:8])
    label = str(row.get("label") or prefix)
    try:
        activity_raw = get_json(with_query(f"{API_BASE}/activity", {"api_key_hash": hash_value}), api_key)
        rows = _unwrap_list(activity_raw, "data", "activity")
        tagged = []
        for record in rows:
            if isinstance(record, dict):
                tagged_record = dict(record)
                tagged_record["_key_prefix"] = prefix
                tagged_record["_key_label"] = label
                tagged.append(tagged_record)
        return tagged, None
    except OpenRouterError as exc:
        return [], f"{prefix}: {exc}"


def fetch_overview(agent=None, *, force: bool = False) -> dict[str, Any]:
    with _OVERVIEW_LOCK:
        settings = load_settings(agent)
        ttl = settings["refresh_interval_minutes"] * 60
        if not force:
            cached = _OVERVIEW_CACHE.get()
            if cached is not None:
                return cached

        key = management_key()
        if not key:
            payload = _empty_payload("missing_management_key")
            _OVERVIEW_CACHE.set(payload, ttl)
            return payload

        aliases = parse_aliases(settings["key_aliases"])
        watched = settings["watched_key_hashes"]
        errors: list[str] = []

        credits: dict[str, Any] = {}
        keys_list: list[Any] = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            credits_future = pool.submit(_fetch_credits, key)
            keys_future = pool.submit(_fetch_keys_list, key)
            try:
                credits = credits_future.result()
            except OpenRouterError as exc:
                errors.append(f"credits: {exc}")
            try:
                keys_list = keys_future.result()
            except OpenRouterError as exc:
                errors.append(f"keys: {exc}")

        normalized_keys: list[dict[str, Any]] = []
        hash_to_label: dict[str, str] = {}
        for item in keys_list:
            if not isinstance(item, dict):
                continue
            hash_value = str(item.get("hash") or item.get("api_key_hash") or item.get("id") or "")
            prefix = hash_value[:8].lower()
            name = str(item.get("name") or "")
            label_field = str(item.get("label") or "")
            display = label_for_key(hash_value, name, label_field, aliases)
            hash_to_label[prefix] = display
            is_watched = not watched or any(
                hash_value.lower().startswith(w) or prefix.startswith(w[:8]) for w in watched
            )
            normalized_keys.append(
                {
                    "hash_prefix": prefix,
                    "hash": hash_value,
                    "label": display,
                    "name": name,
                    "disabled": bool(item.get("disabled")),
                    "limit": item.get("limit"),
                    "usage": item.get("usage"),
                    "watched": is_watched,
                }
            )

        activity_rows: list[dict[str, Any]] = []

        def _ingest_activity(rows: list[Any], row_meta: dict[str, Any]) -> None:
            prefix = row_meta.get("hash_prefix") or ""
            label = row_meta.get("label") or prefix
            for record in rows:
                if isinstance(record, dict):
                    tagged = dict(record)
                    tagged["_key_prefix"] = prefix
                    tagged["_key_label"] = label
                    activity_rows.append(tagged)

        keys_for_activity = [row for row in normalized_keys if row.get("watched")] if watched else []

        if not watched:
            try:
                activity_raw = get_json(f"{API_BASE}/activity", key)
                rows = _unwrap_list(activity_raw, "data", "activity")
                _ingest_activity(rows, {"hash_prefix": "all", "label": "all"})
            except OpenRouterError as exc:
                errors.append(f"aggregate: {exc}")
        else:
            with ThreadPoolExecutor(max_workers=5) as pool:
                futures = [pool.submit(_fetch_key_activity, row, key) for row in keys_for_activity]
                for future in as_completed(futures):
                    records, err = future.result()
                    if err:
                        errors.append(err)
                    activity_rows.extend(records)

        totals = {
            "usd": 0.0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "requests": 0,
        }
        daily: dict[str, dict[str, Any]] = {}
        per_key: dict[str, dict[str, Any]] = {}
        per_model: dict[str, float] = {}
        per_provider: dict[str, float] = {}

        today = datetime.now(timezone.utc).date()
        current_month_start = today.replace(day=1)
        mtd = 0.0

        for record in activity_rows:
            usd = _record_usd(record)
            prompt = _record_tokens(record, "prompt_tokens")
            completion = _record_tokens(record, "completion_tokens")
            reasoning = _record_tokens(record, "reasoning_tokens")
            requests = int(record.get("requests") or record.get("num_requests") or 0)
            label = str(record.get("_key_label") or record.get("_key_prefix") or "unknown")
            day_raw = str(record.get("date") or record.get("day") or "")
            day_key = _date_key(day_raw)
            chart_label = _chart_label(day_key)
            model = str(record.get("model") or record.get("model_permaslug") or "unknown")
            provider = str(record.get("provider_name") or "unknown")

            totals["usd"] += usd
            totals["prompt_tokens"] += prompt
            totals["completion_tokens"] += completion
            totals["reasoning_tokens"] += reasoning
            totals["requests"] += requests

            if day_key:
                try:
                    record_date = date_cls.fromisoformat(day_key)
                    if current_month_start <= record_date <= today:
                        mtd += usd
                except ValueError:
                    pass

                if day_key not in daily:
                    daily[day_key] = {
                        "date": day_key,
                        "label": chart_label,
                        "by_key": {},
                        "total": 0.0,
                    }
                daily[day_key]["by_key"][label] = daily[day_key]["by_key"].get(label, 0.0) + usd
                daily[day_key]["total"] += usd

            bucket = per_key.setdefault(
                label,
                {
                    "label": label,
                    "hash_prefix": record.get("_key_prefix"),
                    "usd": 0.0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "reasoning_tokens": 0,
                    "requests": 0,
                },
            )
            bucket["usd"] += usd
            bucket["prompt_tokens"] += prompt
            bucket["completion_tokens"] += completion
            bucket["reasoning_tokens"] += reasoning
            bucket["requests"] += requests

            per_model[model] = per_model.get(model, 0.0) + usd
            per_provider[provider] = per_provider.get(provider, 0.0) + usd

        daily_series = [v for _, v in sorted(daily.items())]
        per_key_rows = sorted(per_key.values(), key=lambda item: item.get("usd", 0), reverse=True)
        model_rows = sorted(
            [{"model": model, "usd": value} for model, value in per_model.items()],
            key=lambda item: item["usd"],
            reverse=True,
        )
        provider_rows = sorted(
            [{"provider": provider, "usd": value} for provider, value in per_provider.items()],
            key=lambda item: item["usd"],
            reverse=True,
        )

        top_models = model_rows[:12]
        top_keys = per_key_rows[:3]
        top_providers = provider_rows[:6]
        balance = credits.get("total_credits")
        total_usage = credits.get("total_usage")

        days_with_spend = sum(1 for d in daily_series if d["total"] > 0)
        avg_daily = totals["usd"] / max(1, days_with_spend) if days_with_spend else 0.0
        projected_monthly = avg_daily * 30.0

        payload = {
            "ok": True,
            "empty_state": None,
            "credits": {
                "balance": balance,
                "total_usage": total_usage,
                "balance_label": format_usd(float(balance or 0)) if balance is not None else "—",
                "usage_label": format_usd(float(total_usage or 0)) if total_usage is not None else format_usd(totals["usd"]),
            },
            "keys": normalized_keys,
            "totals": {
                **totals,
                "usd_label": format_usd(totals["usd"]),
                "prompt_tokens_label": format_number(totals["prompt_tokens"]),
                "completion_tokens_label": format_number(totals["completion_tokens"]),
                "reasoning_tokens_label": format_number(totals["reasoning_tokens"]),
                "requests_label": format_number(totals["requests"]),
            },
            "summary": {
                "mtd": mtd,
                "mtd_label": format_usd(mtd),
                "avg_daily": avg_daily,
                "avg_daily_label": format_usd(avg_daily),
                "projected_monthly": projected_monthly,
                "projected_monthly_label": format_usd(projected_monthly),
            },
            "daily": daily_series,
            "models": model_rows,
            "top_models": top_models,
            "providers": provider_rows,
            "top_providers": top_providers,
            "per_key": per_key_rows,
            "top_keys": top_keys,
            "hash_to_label": hash_to_label,
            "settings": {
                "default_view": settings["default_view"],
                "show_token_counts": settings["show_token_counts"],
                "refresh_interval_minutes": settings["refresh_interval_minutes"],
            },
            "as_of": datetime.now(timezone.utc).isoformat(),
            "last_error": "; ".join(errors) if errors else None,
            "stale": False,
        }
        _OVERVIEW_CACHE.set(payload, ttl)
        return payload


def fetch_keys(agent=None) -> dict[str, Any]:
    key = management_key()
    if not key:
        return {"ok": False, "keys": [], "error": "Missing OPENROUTER_MANAGEMENT_KEY"}
    settings = load_settings(agent)
    aliases = parse_aliases(settings["key_aliases"])
    keys_raw = get_json(f"{API_BASE}/keys", key)
    keys_list = _unwrap_list(keys_raw, "data", "keys")
    rows = []
    for item in keys_list:
        if not isinstance(item, dict):
            continue
        hash_value = str(item.get("hash") or item.get("api_key_hash") or "")
        prefix = hash_value[:8].lower()
        rows.append(
            {
                "hash_prefix": prefix,
                "hash": hash_value,
                "label": label_for_key(hash_value, str(item.get("name") or ""), str(item.get("label") or ""), aliases),
                "name": item.get("name"),
                "disabled": bool(item.get("disabled")),
            }
        )
    return {"ok": True, "keys": rows}


def invalidate_cache() -> None:
    with _OVERVIEW_LOCK:
        _OVERVIEW_CACHE.clear()
