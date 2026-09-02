"""Shared HTTP helpers."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class HttpError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> Any:
    data = None
    req_headers = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            if not raw.strip():
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise HttpError(f"HTTP {exc.code}: {detail or exc.reason}", exc.code) from exc
    except urllib.error.URLError as exc:
        raise HttpError(f"Connection failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise HttpError("Invalid JSON response") from exc


def join_url(base: str, path: str, params: dict[str, Any] | None = None) -> str:
    base = base.rstrip("/")
    path = path if path.startswith("/") else f"/{path}"
    url = f"{base}{path}"
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if query:
            url = f"{url}?{query}"
    return url
