# AGENTS.md — Agent Zero Plugins (workspace / index staging)

Read this before changing anything here.

## This repo holds no plugin code

The topology is:

| What | Where |
|------|-------|
| **Plugin source of truth** | Each plugin's own repo — files at repo root |
| **Index assets** | `index/<name>/index.yaml` + `thumbnail.webp` here |
| **Index entry** | PR to `agent0ai/a0-plugins` adding `plugins/<name>/index.yaml` (via fork `duketopceo/a0-plugins`) |

Agent Zero clones the **standalone** repo into `/a0/usr/plugins/<name>/` on
install. There is no vendored copy to edit here — the old `plugins/` directory
was removed after it drifted from the standalones in both directions. Do not
re-add vendored plugin trees; a copy made here is stale on arrival.

| Plugin | Standalone repo |
|--------|-----------------|
| `argus` | `duketopceo/a0-plugin-argus` |
| `omaseal` | `duketopceo/a0-plugin-omaseal` |
| `kurultai_people` | `duketopceo/kurultai_people` |
| `openrouter_usage` | `duketopceo/openrouter_usage` |

A behavior change belongs in the standalone repo. This repo changes only when
an index entry is staged or the publish procedure changes.

## Index asset rules (enforced by `agent0ai/a0-plugins` CI)

- One plugin per upstream PR; `plugins/<name>/` may contain only `index.yaml`
  and an optional `thumbnail.<ext>`.
- Folder name: `^[a-z0-9_]+$`, must exactly match `name:` in the standalone
  repo's root `plugin.yaml`.
- `index.yaml`: `title` ≤50, `description` ≤500, `github` repo URL, optional
  `tags` ≤5 and `screenshots` ≤5 full URLs; whole file ≤2000 chars.
- Thumbnail: square, ≤20 KB, `.png/.jpg/.jpeg/.webp`.
- `scripts/validate_index.py` checks the staged `index/` tree for the
  structural subset of these rules; CI runs it on push and PR.

## Conventions

- Bump `version` in the standalone's `plugin.yaml` and tag `vX.Y.Z` there when
  plugin behavior changes — Hub installs track the repo.
- Before staging an `index/<name>/`, the plugin should have run in a real
  Agent Zero install.
- No build step, no package manager, no dependency manifest. Do not add one.
- Not part of the grounding-index family: no `INDEX.md`, no
  `scripts/luke-index-watcher.py`.


## Code graph index (optional accelerator)

This repo may be indexed by `codebase-memory-mcp` (CBM) on an agent's local
machine — `.codebase-memory/` is gitignored. If your harness exposes CBM
tools (`search_graph`, `trace_path`, `get_architecture`, `detect_changes`),
prefer them for structural questions — symbol lookup, caller/callee traces,
impact analysis — instead of grep/read loops. Reindex after large refactors
(`index_repository`); treat `.codebase-memory/graph.db.zst` as a local cache
artifact, never commit it.
