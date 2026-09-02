# Publishing to the Agent Zero Plugin Hub

How to list **Kurultai Memory** and **OpenRouter Usage** in the community [Plugin Index](https://github.com/agent0ai/a0-plugins) so users can install from **Plugins → Browse** inside Agent Zero.

---

## Overview

| What | Where |
|------|--------|
| **Dev monorepo** (this repo) | `plugins/kurultai_people/`, `plugins/openrouter_usage/` |
| **Public plugin repo** (one per plugin) | GitHub repo root = plugin files |
| **Index entry** | PR to `agent0ai/a0-plugins` adding `plugins/<name>/index.yaml` |

The Index points at your GitHub repo. Agent Zero clones that repo into `/a0/usr/plugins/<name>/` on install.

---

## Step 1 — Split into two public repos

Each plugin needs its **own repository** with files at the **root** (not under `plugins/`).

### kurultai_people

```bash
mkdir kurultai_people && cd kurultai_people
cp -r ../agent-zero-plugins/plugins/kurultai_people/* .
git init && git add . && git commit -m "feat: initial kurultai_people plugin"
gh repo create kurultai_people --public --source=. --remote=origin --push
```

### openrouter_usage

```bash
mkdir openrouter_usage && cd openrouter_usage
cp -r ../agent-zero-plugins/plugins/openrouter_usage/* .
git init && git add . && git commit -m "feat: initial openrouter_usage plugin"
gh repo create openrouter_usage --public --source=. --remote=origin --push
```

### Required at repo root

- `plugin.yaml` with `name:` matching folder name exactly (`kurultai_people`, `openrouter_usage`)
- `LICENSE` (MIT — already included)
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

Already in this monorepo under `index/`:

```
index/kurultai_people/index.yaml
index/kurultai_people/thumbnail.webp   # square, < 20 KB
index/openrouter_usage/index.yaml
index/openrouter_usage/thumbnail.webp
```

**Before PR:** update `github:` URLs in each `index.yaml` to your standalone repo URLs.

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

Repeat for `openrouter_usage` in a **separate PR**.

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

## Monorepo vs store repos

| Approach | Use when |
|----------|----------|
| **This monorepo** | You develop both plugins together |
| **Standalone repos** | Required for Plugin Hub listing |
| **Sync script** (optional) | `rsync -a plugins/kurultai_people/ ../kurultai_people/` before release tag |

Tag releases on standalone repos (`v1.1.0`) so Hub installs can pin versions.

---

## Quick reference

- Plugin Index: https://github.com/agent0ai/a0-plugins
- Agent Zero plugin docs: https://github.com/agent0ai/agent-zero/tree/main/docs/guides
- Create plugin guide: https://github.com/agent0ai/agent-zero/blob/main/docs/guides/create-plugin.md
