"""Normalize Kurultai search hits for agents and UI."""

from __future__ import annotations

from typing import Any


def snippet_from_atom(atom: dict[str, Any], max_chars: int) -> str:
    for key in ("summary", "content", "question"):
        value = atom.get(key)
        if isinstance(value, str) and value.strip():
            text = value.strip()
            if len(text) <= max_chars:
                return text
            return text[: max_chars - 1].rstrip() + "…"
    return ""


def normalize_search_results(payload: Any, max_chars: int) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []
    hits: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        atom = item.get("atom") if isinstance(item.get("atom"), dict) else item
        if not isinstance(atom, dict):
            continue
        hits.append(
            {
                "title": str(atom.get("title") or "Untitled"),
                "snippet": snippet_from_atom(atom, max_chars),
                "source": str(atom.get("source") or ""),
                "source_id": str(atom.get("source_id") or ""),
                "score": float(item.get("score") or 0),
                "tags": atom.get("tags") if isinstance(atom.get("tags"), list) else [],
                "metadata": {
                    "rank": item.get("rank"),
                    "matched_by": item.get("matched_by"),
                },
            }
        )
    return hits


def normalize_who_knows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict):
            rows.append(
                {
                    "source": str(item.get("source") or item.get("name") or ""),
                    "count": item.get("count") or item.get("atoms") or item.get("hits"),
                    "topic": item.get("topic"),
                }
            )
    return rows


def normalize_citation(payload: Any, max_chars: int) -> dict[str, Any] | None:
    if payload is None:
        return None
    if isinstance(payload, dict):
        if "atom" in payload and isinstance(payload["atom"], dict):
            atom = payload["atom"]
            return {
                "title": str(atom.get("title") or "Untitled"),
                "snippet": snippet_from_atom(atom, max_chars),
                "source": str(atom.get("source") or payload.get("source") or ""),
                "source_id": str(atom.get("source_id") or payload.get("source_id") or ""),
            }
        excerpt = payload.get("excerpt") or payload.get("snippet")
        if isinstance(excerpt, str):
            return {
                "title": str(payload.get("title") or "Citation"),
                "snippet": excerpt[:max_chars],
                "source": str(payload.get("source") or ""),
                "source_id": str(payload.get("source_id") or ""),
            }
    return None


def format_citation_for_agent(citation: dict[str, Any] | None) -> str:
    if not citation:
        return "No citation found in Kurultai."
    return "\n".join(
        [
            citation.get("title", "Citation"),
            f"source: {citation.get('source', '')} / {citation.get('source_id', '')}",
            citation.get("snippet", ""),
        ]
    )


def format_hits_for_agent(hits: list[dict[str, Any]]) -> str:
    if not hits:
        return "No matches in Kurultai."
    blocks: list[str] = []
    for index, hit in enumerate(hits, start=1):
        source_ref = hit.get("source_id") or hit.get("source") or "unknown"
        blocks.append(
            "\n".join(
                [
                    f"{index}. {hit.get('title', 'Untitled')} (score {hit.get('score', 0):.2f})",
                    f"   source: {hit.get('source', '')} / {source_ref}",
                    f"   {hit.get('snippet', '')}",
                ]
            )
        )
    return "\n\n".join(blocks)
