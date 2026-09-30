# Agent Zero Plugins — workspace

Hub-side workspace for [@duketopceo](https://github.com/duketopceo)'s
[Agent Zero](https://github.com/agent0ai/agent-zero) plugins.

**Plugin source of truth = the standalone repos.** Agent Zero clones a
plugin's own repo into `/a0/usr/plugins/<name>/` on install, so each plugin
lives at the root of its own repository — no plugin code is kept here.

| Plugin | Repo | Hub |
|--------|------|-----|
| **Argus PR Reviewer** | [duketopceo/a0-plugin-argus](https://github.com/duketopceo/a0-plugin-argus) | pending |
| **OmaSeal Secrets** | [duketopceo/a0-plugin-omaseal](https://github.com/duketopceo/a0-plugin-omaseal) | pending |
| **Kurultai Memory** | [duketopceo/kurultai_people](https://github.com/duketopceo/kurultai_people) | ✅ listed |
| **OpenRouter Usage** | [duketopceo/openrouter_usage](https://github.com/duketopceo/openrouter_usage) | ✅ listed |

## What's here

- `index/<name>/` — staged Plugin Hub assets (`index.yaml` + `thumbnail.webp`)
- `docs/PUBLISHING.md` — the publish procedure, current
- `docs/plans/` — roadmap plans
- `scripts/validate_index.py` — offline check of staged assets against Hub rules (runs in CI)

## Flow

1. Develop in the standalone repo (tests, version bump, tag).
2. Stage/update `index/<name>/` here.
3. PR `plugins/<name>/` to the fork `duketopceo/a0-plugins` → upstream
   `agent0ai/a0-plugins`. One plugin per PR.
