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
