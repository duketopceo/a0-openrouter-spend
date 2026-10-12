# Landscape: a0-openrouter-spend (2026-10-11)

Question: what is this repo for today, who else does it, and what should it become? Code and docs read first (`README.md`, `AGENTS.md`, `docs/PUBLISHING.md`, `scripts/validate_index.py`, `index/*`, git history).

## What this repo is now

It is not an OpenRouter spend plugin, despite its name and its GitHub description ("Agent Zero plugin: OpenRouter organisation spend widget and dashboard, authenticated with a management key"). It began as an authoring monorepo for two plugins (history: PRs #3 and #4). Since #8 (2026-09-30) it holds no plugin code. What remains:

- `index/<name>/index.yaml` plus `thumbnail.webp` for four plugins: `argus`, `omaseal`, `kurultai_people`, `openrouter_usage`.
- `docs/PUBLISHING.md`, the procedure for the Agent Zero Plugin Hub.
- `scripts/validate_index.py` (94 lines, structural subset, offline) run by `.github/workflows/ci.yml`.

The spend plugin itself is `duketopceo/openrouter_usage`. For background, OpenRouter's [credits endpoint](https://openrouter.ai/docs/api/api-reference/credits/get-remaining-credits.md) is documented as requiring a management key; community sources say regular keys get 401 on analytics endpoints (unverified, community-sourced).

## Comparables

| Thing | What it does | Compared with this repo |
|---|---|---|
| [agent0ai/a0-plugins](https://github.com/agent0ai/a0-plugins) | The upstream Plugin Index. One plugin per PR, folder `plugins/<name>/` with `index.yaml` (title 50, description 500, `github`, 5 tags, 5 screenshots, 2000 chars total) and optional square thumbnail of 20 KB or less; CI checks the remote repo's `plugin.yaml` name | The authority. This repo mirrors its rules offline but cannot check the remote `plugin.yaml` |
| Your fork `duketopceo/a0-plugins` | Where submission PRs are made from | Could hold the staging branches directly, making this repo redundant |

I found no other project that stages a plugin-index submission in a separate repo; the pattern appears specific to this setup. Treat the comparison as thin by design.

## What users (the owner and agents) expect

- One place that says what is listed, pending or retired. `README.md` and `docs/PUBLISHING.md` have that table; it is manual.
- CI that stops a bad card before an upstream PR wastes a maintainer's time (upstream may close PRs that keep failing for 7+ days, per the a0-plugins README).

## What is unique

Almost nothing, and that is the finding. The repo's value is (1) the offline validator and (2) the staged thumbnails. Both are small.

## Gaps and risks

- Identity mismatch: name, GitHub description and `docs/plans/2026-09-05---a0-plugins-ui-ux-overhaul.md` still describe an authoring monorepo.
- The validator does not check the thumbnail is square, tags against upstream `TAGS.md`, or that `github:` repos' `plugin.yaml` name matches the folder (upstream CI does).
- The status table is hand-maintained and has drifted before (see the earlier source-of-truth plan).
