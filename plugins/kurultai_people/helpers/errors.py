"""User-readable Kurultai errors."""

from __future__ import annotations

from usr.plugins.kurultai_people.helpers.http_util import HttpError


def friendly_error(exc: Exception, base_url: str = "") -> str:
    if isinstance(exc, HttpError):
        if exc.status == 401 or exc.status == 403:
            return "Kurultai rejected credentials. Check KURULTAI_API_KEY in Agent Zero Secrets."
        if exc.status == 404:
            return "Kurultai endpoint not found. Check kurultai_base_url and that the daemon is running."
        if exc.status and exc.status >= 500:
            return "Kurultai returned a server error. Try again later."
        return str(exc)
    message = str(exc).strip() or exc.__class__.__name__
    if "Connection failed" in message or "timed out" in message.lower():
        host = base_url or "configured host"
        return f"Kurultai is unreachable at {host}. Check kurultai_base_url."
    return message
