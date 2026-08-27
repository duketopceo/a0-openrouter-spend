"""Kurultai HTTP and optional MCP client."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from helpers.plugins import get_plugin_config
from helpers.secrets import get_secrets_manager
from usr.plugins.kurultai_people.helpers.http_util import HttpError, join_url, request_json
from usr.plugins.kurultai_people.helpers.normalize import (
    normalize_search_results,
    normalize_who_knows,
)

_PERSON_QUERY = re.compile(
    r"(?i)(^who\s+(is|works|knows)|@|\bteam\b|\brole\b|\bemail\b|\broster\b|\bcontact\b)"
)


def load_settings(agent=None) -> dict[str, Any]:
    config = get_plugin_config("kurultai_people", agent=agent) or {}
    secrets = get_secrets_manager().load_secrets()
    api_key = secrets.get("KURULTAI_API_KEY", "").strip()
    return {
        "base_url": str(config.get("kurultai_base_url") or "").strip().rstrip("/"),
        "mcp_url": str(config.get("kurultai_mcp_url") or "").strip().rstrip("/"),
        "timeout": float(config.get("timeout_seconds") or 15),
        "max_results": int(config.get("max_results") or 8),
        "snippet_max_chars": int(config.get("snippet_max_chars") or 400),
        "test_query": str(config.get("test_query") or "Luke Duke"),
        "api_key": api_key,
    }


def is_people_query(query: str) -> bool:
    return bool(_PERSON_QUERY.search(query or ""))


def _auth_headers(api_key: str) -> dict[str, str]:
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def _mcp_call(settings: dict[str, Any], tool_name: str, arguments: dict[str, Any]) -> Any:
    mcp_url = settings.get("mcp_url") or ""
    if not mcp_url:
        raise HttpError("kurultai_mcp_url is not configured")
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    response = request_json(
        "POST",
        mcp_url,
        headers=_auth_headers(settings.get("api_key", "")),
        body=payload,
        timeout=settings.get("timeout", 15),
    )
    if not isinstance(response, dict):
        raise HttpError("Invalid MCP response")
    if response.get("error"):
        err = response["error"]
        message = err.get("message") if isinstance(err, dict) else str(err)
        raise HttpError(message or "MCP tool call failed")
    result = response.get("result")
    if isinstance(result, dict) and "content" in result:
        content = result.get("content")
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict) and isinstance(first.get("text"), str):
                try:
                    return json.loads(first["text"])
                except json.JSONDecodeError:
                    return first["text"]
    return result


def search_http(settings: dict[str, Any], query: str, limit: int, source: str | None = None) -> list[dict[str, Any]]:
    base = settings.get("base_url") or ""
    if not base:
        raise HttpError("kurultai_base_url is not configured")
    headers = _auth_headers(settings.get("api_key", ""))
    timeout = settings.get("timeout", 15)
    params = {"q": query, "limit": limit}
    if source:
        params["source"] = source
    try:
        payload = request_json("GET", join_url(base, "/api/search", params), headers=headers, timeout=timeout)
    except HttpError as exc:
        if exc.status not in (405, 404):
            raise
        payload = request_json(
            "POST",
            join_url(base, "/api/search"),
            headers=headers,
            body={"query": query, "limit": limit, "source": source},
            timeout=timeout,
        )
    return normalize_search_results(payload, settings.get("snippet_max_chars", 400))


def who_knows_http(settings: dict[str, Any], topic: str, limit: int) -> list[dict[str, Any]]:
    base = settings.get("base_url") or ""
    if not base:
        raise HttpError("kurultai_base_url is not configured")
    payload = request_json(
        "POST",
        join_url(base, "/who_knows"),
        headers=_auth_headers(settings.get("api_key", "")),
        body={"topic": topic, "limit": limit},
        timeout=settings.get("timeout", 15),
    )
    return normalize_who_knows(payload)


def kurultai_search(
    agent,
    query: str,
    *,
    scope: str = "",
    source: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    settings = load_settings(agent)
    if not query.strip():
        raise HttpError("Query is required")
    max_results = limit or settings.get("max_results", 8)
    use_people = scope == "people" or (not scope and is_people_query(query))
    hits: list[dict[str, Any]] = []
    who_knows: list[dict[str, Any]] = []

    if settings.get("mcp_url"):
        tool = "who_knows" if use_people else "search"
        args = (
            {"topic": query, "limit": max_results}
            if tool == "who_knows"
            else {"query": query, "limit": max_results, **({"source": source} if source else {})}
        )
        payload = _mcp_call(settings, tool, args)
        if tool == "who_knows":
            who_knows = normalize_who_knows(payload)
        else:
            hits = normalize_search_results(payload, settings.get("snippet_max_chars", 400))
    else:
        if use_people:
            try:
                who_knows = who_knows_http(settings, query, max_results)
            except HttpError:
                who_knows = []
        hits = search_http(settings, query, max_results, source=source)

    return {"query": query, "scope": "people" if use_people else "general", "hits": hits, "who_knows": who_knows}


def test_connection(agent) -> dict[str, Any]:
    settings = load_settings(agent)
    base = settings.get("base_url") or ""
    if not base and not settings.get("mcp_url"):
        raise HttpError("Set kurultai_base_url or kurultai_mcp_url in plugin settings")
    status: dict[str, Any] = {"ok": True}
    if base:
        try:
            status_payload = request_json(
                "GET",
                join_url(base, "/api/status"),
                headers=_auth_headers(settings.get("api_key", "")),
                timeout=settings.get("timeout", 15),
            )
            if isinstance(status_payload, dict):
                status["status"] = status_payload
        except HttpError:
            request_json(
                "GET",
                join_url(base, "/health"),
                headers=_auth_headers(settings.get("api_key", "")),
                timeout=settings.get("timeout", 15),
            )
    result = kurultai_search(agent, settings.get("test_query", "Luke Duke"))
    status["sample"] = result
    return status
