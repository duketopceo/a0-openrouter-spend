# Publishing to the Agent Zero Plugin Hub

How to list a plugin in the community [Plugin Index](https://github.com/agent0ai/a0-plugins) so users can install from **Plugins → Browse** inside Agent Zero.

---

## Overview

| What | Where |
|------|--------|
| **Plugin source of truth** | One repo per plugin — files at repo root |
| **Index assets** (this repo) | `index/<name>/index.yaml` + `thumbnail.webp` |
| **Index entry** | PR to `agent0ai/a0-plugins` adding `plugins/<name>/index.yaml` |

The Index points at your GitHub repo. Agent Zero clones that repo into `/a0/usr/plugins/<name>/` on install.

Current plugins and their repos:

| Plugin | Repo | Hub |
|--------|------|-----|
| `argus` | `duketopceo/a0-plugin-argus` | pending |
| `omaseal` | `duketopceo/a0-plugin-omaseal` | pending |
| `kurultai_people` | `duketopceo/kurultai_people` | listed |
| `openrouter_usage` | `duketopceo/openrouter_usage` | listed |

---

## Step 1 — Plugin repo requirements

Each plugin's **own repository** holds the plugin files at the **root**.
Required there:

- `plugin.yaml` with `name:` matching the index folder name exactly
- `LICENSE` (MIT)
- `README.md`

Verify:

```bash
curl -s https://raw.githubusercontent.com/YOU/kurultai_people/main/plugin.yaml | grep '^name:'
# name: kurultai_people
```

---

## Step 2 — Pre-flight review

Run locally in Agent Zero, then audit with the review skill:

1. Copy to `/a0/usr/plugins/`, enable, configure, smoke-test
2. Review checklist: manifest, Store Gate, no secrets in git, notifications not inline errors

Fix any FAIL items before submitting.

---

## Step 3 — Prepare index assets

Staged in this repo under `index/`:

```
index/<name>/index.yaml
index/<name>/thumbnail.webp   # square, < 20 KB
```

`scripts/validate_index.py` checks the staged tree (also runs in CI).
**Before PR:** verify `github:` in each `index.yaml` points at the plugin's standalone repo.

**Screenshots:** optional URLs in `index.yaml` (max 5). Use raw GitHub URLs to `docs/logo.webp` or real UI screenshots.

**Tags:** pick from [TAGS.md](https://github.com/agent0ai/a0-plugins/blob/main/TAGS.md) (max 5).

Check name is free:

```bash
curl -sL https://github.com/agent0ai/a0-plugins/releases/download/generated-index/index.json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('kurultai_people' in d.get('plugins',{}))"
```

---

## Step 4 — Open Index PR (one plugin per PR)

```bash
gh repo fork agent0ai/a0-plugins --clone
cd a0-plugins
git checkout -b add-kurultai_people

mkdir -p plugins/kurultai_people
cp /path/to/index/kurultai_people/index.yaml plugins/kurultai_people/
cp /path/to/index/kurultai_people/thumbnail.webp plugins/kurultai_people/

git add plugins/kurultai_people/
git commit -m "feat: add kurultai_people plugin"
git push origin add-kurultai_people

gh pr create --repo agent0ai/a0-plugins \
  --title "feat: add kurultai_people" \
  --body "Kurultai Memory — search, recall, and cite indexed knowledge.

- GitHub: https://github.com/YOU/kurultai_people
- Tags: tools, search, memory, external"
```

Repeat for each plugin in a **separate PR**.

### CI rules (common failures)

| Rule | Requirement |
|------|-------------|
| Folder name | `^[a-z0-9_]+$`, matches remote `plugin.yaml` `name` |
| `index.yaml` only | Plus optional `thumbnail.{png,jpg,webp}` — nothing else in folder |
| `title` | ≤ 50 chars |
| `description` | ≤ 500 chars |
| Thumbnail | Square, ≤ 20 KB |
| Remote repo | Public, `LICENSE` + `plugin.yaml` at root |
| One plugin | One new folder per PR |

---

## Step 5 — After merge

Users find plugins in Agent Zero:

**Plugins → Browse** (Plugin Hub) → search → **Install**

Installed path: `/a0/usr/plugins/<name>/`

---

## Standalone repos are canonical

There is no dev monorepo. A vendored copy under `plugins/` was removed after
drifting from the standalones in both directions — every copy is stale on
arrival. Develop in the standalone repo, bump `version` in `plugin.yaml`, and
tag releases there (`vX.Y.Z`) so Hub installs can pin versions.

---

## Quick reference

- Plugin Index: https://github.com/agent0ai/a0-plugins
- Agent Zero plugin docs: https://github.com/agent0ai/agent-zero/tree/main/docs/guides
- Create plugin guide: https://github.com/agent0ai/agent-zero/blob/main/docs/guides/create-plugin.md
