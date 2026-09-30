#!/usr/bin/env python3
"""Validate index/<name>/ assets against the agent0ai/a0-plugins submission
rules (structural subset — no network). Run from repo root:
    python3 scripts/validate_index.py
"""
import re
import sys
from pathlib import Path

import yaml

INDEX_DIR = Path("index")
NAME_RE = re.compile(r"^[a-z0-9_]+$")
ALLOWED_FIELDS = {"title", "description", "github", "tags", "screenshots"}
REQUIRED_FIELDS = {"title", "description", "github"}
THUMBNAIL_MAX = 20 * 1024
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
FAILURES = []


def fail(name: str, msg: str) -> None:
    FAILURES.append(f"{name}: {msg}")


def check_plugin(folder: Path) -> None:
    name = folder.name
    if not NAME_RE.match(name) or name.startswith("_"):
        fail(name, "folder name must match ^[a-z0-9_]+$ and not start with '_'")

    index_yaml = folder / "index.yaml"
    if not index_yaml.exists():
        fail(name, "missing index.yaml")
        return
    if len(index_yaml.read_text()) > 2000:
        fail(name, "index.yaml exceeds 2000 chars")

    data = yaml.safe_load(index_yaml.read_text())
    if not isinstance(data, dict):
        fail(name, "index.yaml is not a mapping")
        return

    for field in REQUIRED_FIELDS:
        if not data.get(field):
            fail(name, f"missing required field '{field}'")
    for field in data:
        if field not in ALLOWED_FIELDS:
            fail(name, f"unknown field '{field}' (allowed: {sorted(ALLOWED_FIELDS)})")

    if len(str(data.get("title", ""))) > 50:
        fail(name, "title exceeds 50 chars")
    if len(str(data.get("description", ""))) > 500:
        fail(name, "description exceeds 500 chars")
    github = str(data.get("github", ""))
    if github and not re.match(r"^https://github\.com/[\w.-]+/[\w.-]+/?$", github):
        fail(name, f"github field is not a repo URL: {github}")

    tags = data.get("tags", [])
    if tags and (not isinstance(tags, list) or len(tags) > 5
                 or not all(isinstance(t, str) for t in tags)):
        fail(name, "tags must be a list of up to 5 strings")

    shots = data.get("screenshots", [])
    if shots and (not isinstance(shots, list) or len(shots) > 5
                  or not all(str(s).startswith("http") for s in shots)):
        fail(name, "screenshots must be up to 5 full URLs")

    thumbs = [p for p in folder.iterdir() if p.stem == "thumbnail"]
    extra = [p for p in folder.iterdir()
             if p.name != "index.yaml" and p not in thumbs]
    if extra:
        fail(name, f"unexpected files: {[p.name for p in extra]}")
    for t in thumbs:
        if t.suffix.lower() not in IMG_EXTS:
            fail(name, f"thumbnail ext {t.suffix} not allowed")
        elif t.stat().st_size > THUMBNAIL_MAX:
            fail(name, f"thumbnail {t.name} is {t.stat().st_size}B > 20KB")


def main() -> int:
    folders = [p for p in INDEX_DIR.iterdir() if p.is_dir()] if INDEX_DIR.is_dir() else []
    if not folders:
        print("no index/ plugin folders found")
        return 0
    for folder in folders:
        check_plugin(folder)
    if FAILURES:
        print("\n".join(FAILURES))
        return 1
    print(f"ok: {len(folders)} index asset(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
