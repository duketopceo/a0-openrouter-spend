"""Kurultai HTTP and optional MCP client — search, recall, cite."""

from __future__ import annotations

import json
import os
import re
import uuid
from typing import Any

from helpers.plugins import get_plugin_config
from helpers.secrets import get_secrets_manager
from usr.plugins.kurultai_people.helpers.http_util import HttpError, join_url, request_json
from usr.plugins.kurultai_people.helpers.normalize import (
    normalize_citation,
    normalize_search_results,
    normalize_who_knows,
)

_PERSON_QUERY = re.compile(
    r"(?i)(^who\s+(is|works|knows)|@|\bteam\b|\brole\b|\bemail\b|\broster\b|\bcontact\b)"
)
_MEMORY_QUERY = re.compile(
    r"(?i)(\bremember\b|\brecall\b|\bwhat did we\b|\bprevious(ly)?\b|\bearlier\b|\blast time\b|\bnotes?\b|\bbrain\b)"
)


def load_settings(agent=None) -> dict[str, Any]:
    config = get_plugin_config("kurultai_people", agent=agent) or {}
    secrets = get_secrets_manager().load_secrets()
    api_key = secrets.get("KURULTAI_API_KEY", "").strip()
    project = str(config.get("kurultai_project") or os.environ.get("KURULTAI_PROJECT") or "").strip()
    return {
        "base_url": str(config.get("kurultai_base_url") or "").strip().rstrip("/"),
        "mcp_url": str(config.get("kurultai_mcp_url") or "").strip().rstrip("/"),
        "project": project,
        "timeout": float(config.get("timeout_seconds") or 15),
        "max_results": int(config.get("max_results") or 8),
        "snippet_max_chars": int(config.get("snippet_max_chars") or 400),
        "test_query": str(config.get("test_query") or "Luke Duke"),
        "prefer_recall_for_memory": bool(config.get("prefer_recall_for_memory", True)),
        "api_key": api_key,
    }


def is_people_query(query: str) -> bool:
    return bool(_PERSON_QUERY.search(query or ""))


def is_memory_query(query: str) -> bool:
    return bool(_MEMORY_QUERY.search(query or ""))


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


def recall_http(
    settings: dict[str, Any],
    query: str,
    limit: int,
    project: str | None = None,
) -> list[dict[str, Any]]:
    base = settings.get("base_url") or ""
    if not base:
        raise HttpError("kurultai_base_url is not configured")
    body: dict[str, Any] = {"query": query, "limit": limit}
    if project:
        body["project"] = project
    payload = request_json(
        "POST",
        join_url(base, "/api/recall"),
        headers=_auth_headers(settings.get("api_key", "")),
        body=body,
        timeout=settings.get("timeout", 15),
    )
    return normalize_search_results(payload, settings.get("snippet_max_chars", 400))


def cite_http(settings: dict[str, Any], source: str, source_id: str) -> dict[str, Any] | None:
    base = settings.get("base_url") or ""
    if not base:
        raise HttpError("kurultai_base_url is not configured")
    payload = request_json(
        "POST",
        join_url(base, "/cite"),
        headers=_auth_headers(settings.get("api_key", "")),
        body={"source": source, "source_id": source_id},
        timeout=settings.get("timeout", 15),
    )
    return normalize_citation(payload, settings.get("snippet_max_chars", 400))


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
    use_recall = scope == "memory" or (
        settings.get("prefer_recall_for_memory") and is_memory_query(query) and not use_people
    )
    hits: list[dict[str, Any]] = []
    who_knows: list[dict[str, Any]] = []

    if settings.get("mcp_url"):
        if use_recall:
            tool = "recall"
            args = {
                "query": query,
                "limit": max_results,
                **({"project": settings["project"]} if settings.get("project") else {}),
            }
        elif use_people:
            tool = "who_knows"
            args = {"topic": query, "limit": max_results}
        else:
            tool = "search"
            args = {"query": query, "limit": max_results, **({"source": source} if source else {})}
        payload = _mcp_call(settings, tool, args)
        if tool == "who_knows":
            who_knows = normalize_who_knows(payload)
        else:
            hits = normalize_search_results(payload, settings.get("snippet_max_chars", 400))
    else:
        if use_recall:
            hits = recall_http(settings, query, max_results, project=settings.get("project") or None)
        else:
            if use_people:
                try:
                    who_knows = who_knows_http(settings, query, max_results)
                except HttpError:
                    who_knows = []
            hits = search_http(settings, query, max_results, source=source)

    resolved_scope = "people" if use_people else ("memory" if use_recall else "general")
    return {"query": query, "scope": resolved_scope, "hits": hits, "who_knows": who_knows}


def kurultai_recall(agent, query: str, *, project: str = "", limit: int | None = None) -> dict[str, Any]:
    settings = load_settings(agent)
    if not query.strip():
        raise HttpError("Query is required")
    max_results = limit or settings.get("max_results", 8)
    project_name = (project or settings.get("project") or "").strip() or None
    if settings.get("mcp_url"):
        payload = _mcp_call(
            settings,
            "recall",
            {
                "query": query,
                "limit": max_results,
                **({"project": project_name} if project_name else {}),
            },
        )
        hits = normalize_search_results(payload, settings.get("snippet_max_chars", 400))
    else:
        hits = recall_http(settings, query, max_results, project=project_name)
    return {"query": query, "project": project_name or "default", "hits": hits}


def kurultai_cite(agent, source: str, source_id: str) -> dict[str, Any]:
    settings = load_settings(agent)
    if not source.strip() or not source_id.strip():
        raise HttpError("Both source and source_id are required")
    if settings.get("mcp_url"):
        payload = _mcp_call(settings, "cite", {"source": source, "source_id": source_id})
        citation = normalize_citation(payload, settings.get("snippet_max_chars", 400))
    else:
        citation = cite_http(settings, source, source_id)
    return {"citation": citation}


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
