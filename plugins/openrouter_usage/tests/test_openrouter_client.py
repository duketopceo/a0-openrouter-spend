"""Standalone tests for openrouter_client.py.

Run directly with:
    python3 plugins/openrouter_usage/tests/test_openrouter_client.py

Or with pytest if it is installed:
    pytest plugins/openrouter_usage/tests/test_openrouter_client.py
"""

from __future__ import annotations

import importlib.util
import sys
import types
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock


def _load_test_modules() -> types.ModuleType:
    """Inject the helpers/ and usr/ packages required by the plugin."""
    helpers = types.ModuleType("helpers")
    helpers.plugins = types.ModuleType("helpers.plugins")
    helpers.secrets = types.ModuleType("helpers.secrets")

    def _get_plugin_config(name: str, agent=None):
        return {
            "watched_key_hashes": [],
            "key_aliases": "",
            "refresh_interval_minutes": 5,
            "default_view": "simple",
            "show_token_counts": True,
        }

    def _get_secrets_manager():
        m = MagicMock()
        m.load_secrets.return_value = {"OPENROUTER_MANAGEMENT_KEY": "test-key"}
        return m

    helpers.plugins.get_plugin_config = _get_plugin_config
    helpers.secrets.get_secrets_manager = _get_secrets_manager

    sys.modules["helpers"] = helpers
    sys.modules["helpers.plugins"] = helpers.plugins
    sys.modules["helpers.secrets"] = helpers.secrets

    usr = types.ModuleType("usr")
    usr.plugins = types.ModuleType("usr.plugins")
    usr.plugins.openrouter_usage = types.ModuleType("usr.plugins.openrouter_usage")
    usr.plugins.openrouter_usage.helpers = types.ModuleType("usr.plugins.openrouter_usage.helpers")

    sys.modules["usr"] = usr
    sys.modules["usr.plugins"] = usr.plugins
    sys.modules["usr.plugins.openrouter_usage"] = usr.plugins.openrouter_usage
    sys.modules["usr.plugins.openrouter_usage.helpers"] = usr.plugins.openrouter_usage.helpers

    def _load(name: str, path: str) -> types.ModuleType:
        spec = importlib.util.spec_from_file_location(
            f"usr.plugins.openrouter_usage.helpers.{name}", path
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod.__name__] = mod
        spec.loader.exec_module(mod)
        return mod

    base = "plugins/openrouter_usage/helpers"
    _load("aliases", f"{base}/aliases.py")
    _load("cache", f"{base}/cache.py")
    _load("format", f"{base}/format.py")
    _load("fetch", f"{base}/fetch.py")
    return _load("openrouter_client", f"{base}/openrouter_client.py")


client = _load_test_modules()


def _make_today_record() -> dict:
    today = datetime.now(timezone.utc).date()
    return {
        "date": today.isoformat(),
        "usage": 1.5,
        "prompt_tokens": 1000,
        "completion_tokens": 200,
        "reasoning_tokens": 50,
        "requests": 42,
        "model": "openai/gpt-4",
        "provider_name": "OpenAI",
    }


def _fake_get_json_factory(record: dict):
    def fake_get_json(url: str, _key: str):
        if "/credits" in url:
            return {"data": {"total_credits": 100, "total_usage": 55.5}}
        if "/keys" in url and "/activity" not in url:
            return {"data": [{"hash": "abc123456789", "name": "test", "label": "t", "usage": 2.5, "disabled": False}]}
        if "/activity" in url:
            return {"data": [record]}
        raise ValueError(f"unexpected URL: {url}")
    return fake_get_json


def test_fetch_overview_computes_payload() -> None:
    record = _make_today_record()
    client.get_json = _fake_get_json_factory(record)
    payload = client.fetch_overview(force=True)

    assert payload["ok"] is True, f"expected ok=True, got {payload.get('ok')}"
    assert payload["empty_state"] is None
    assert payload["credits"]["balance"] == 100
    assert payload["credits"]["balance_label"] == "$100.00"
    assert payload["credits"]["usage_label"] == "$55.50"
    assert round(payload["totals"]["usd"], 2) == 1.5
    assert payload["totals"]["requests"] == 42
    assert payload["totals"]["prompt_tokens"] == 1000
    assert payload["summary"]["mtd"] == 1.5
    assert payload["summary"]["mtd_label"] == "$1.50"
    assert len(payload["daily"]) == 1
    assert round(payload["daily"][0]["total"], 2) == 1.5
    assert payload["daily"][0]["by_key"]["all"] == 1.5
    assert len(payload["models"]) == 1
    assert payload["models"][0]["model"] == "openai/gpt-4"
    assert payload["providers"][0]["provider"] == "OpenAI"
    assert payload["per_key"][0]["label"] == "all"
    assert payload["per_key"][0]["usd"] == 1.5


def test_fetch_overview_watched_key() -> None:
    record = _make_today_record()
    # Override the settings to watch the key
    original_get_config = client.get_plugin_config
    client.get_plugin_config = lambda name, agent=None: {
        "watched_key_hashes": ["abc12345"],
        "key_aliases": "",
        "refresh_interval_minutes": 5,
        "default_view": "simple",
        "show_token_counts": True,
    }
    try:
        client.get_json = _fake_get_json_factory(record)
        client.invalidate_cache()
        payload = client.fetch_overview(force=True)
        assert payload["ok"] is True
        # The single key should be watched and its activity ingested per-key
        assert len(payload["per_key"]) == 1
        assert payload["per_key"][0]["hash_prefix"] == "abc12345"
        assert payload["per_key"][0]["usd"] == 1.5
    finally:
        client.get_plugin_config = original_get_config
        client.invalidate_cache()


def test_format_helpers() -> None:
    assert client.format_usd(1.2) == "$1.20"
    assert client.format_usd(0.001) == "$0.0010"
    assert client.format_usd(float("nan")) == "—"
    assert client.format_number(1234567) == "1,234,567"


def _run_all() -> int:
    tests = [
        test_fetch_overview_computes_payload,
        test_fetch_overview_watched_key,
        test_format_helpers,
    ]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {test.__name__}: {exc}")
        except Exception as exc:
            failures += 1
            print(f"ERR   {test.__name__}: {exc}")
    return failures


if __name__ == "__main__":
    failures = _run_all()
    if failures:
        print(f"\n{failures} test(s) failed.")
        sys.exit(1)
    print("\nAll tests passed.")
    sys.exit(0)
