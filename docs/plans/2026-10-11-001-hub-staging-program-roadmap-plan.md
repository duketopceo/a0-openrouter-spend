---
title: "a0-openrouter-spend program roadmap"
type: program-roadmap
status: proposed
date: 2026-10-11
origin: docs/research/2026-10-11-landscape.md
---

# a0-openrouter-spend program roadmap

> Written by hand (`compound-engineering:ce-plan` not run; docs-only pass on a tiny repo). Claims checked against the repo on 2026-10-11.

## Summary

This repo is a staging area for Plugin Hub cards, not a plugin. Fix its identity, make the validator match upstream CI, get the two pending plugins listed, then archive it.

## Now / Next / Later

| ID | Unit | Horizon | Difficulty |
|---|---|---|---|
| U1 | Fix identity: GitHub description and plan headers | Now | easy |
| U2 | Validator parity with upstream CI (square, TAGS.md, remote plugin.yaml name) | Now | medium |
| U3 | Submit `argus` and `omaseal` to the Hub with the Patchbay thumbnails | Next | easy |
| U4 | Mark done plans as done, delete the superseded UI plan | Next | easy |
| U5 | Archive this repo once all four plugins are listed | Later | easy |

## Units

### U1. Fix identity
- Status: Now. Evidence: GitHub description says "OpenRouter organisation spend widget and dashboard"; the repo holds no plugin code (`AGENTS.md`).
- Verification: description matches `README.md`. **Difficulty**: easy.
- **Feasibility**: changing a repo description is a settings change that this program must not make; it is an owner action. Renaming the repo would break `git remote` URLs (GitHub redirects, but docs link to the old name).
- **Simpler alternative**: leave the name, fix only the description (`gh repo edit --description`).

### U2. Validator parity with upstream
- Status: Now. Evidence: `scripts/validate_index.py` checks fields, lengths, extensions and 20 KB; upstream also requires a square thumbnail, tags from `TAGS.md`, and a matching remote `plugin.yaml` `name` ([a0-plugins](https://github.com/agent0ai/a0-plugins)).
- Dependencies: network for the last two checks; keep them opt-in (`--online`) so CI stays offline. Verification: a card with a wrong tag fails.
- **Difficulty**: medium. Square check needs image dimensions: webp header parse without Pillow (about 15 lines) or add Pillow to CI.
- **Feasibility**: `TAGS.md` can change upstream; fetch it at run time rather than copying it.
- **Simpler alternative**: run upstream's own CI by opening a draft PR on the fork; delete the validator.

### U3. Submit argus and omaseal
- Status: Next. Evidence: README table says "pending" for both; `docs/HANDOFF.md` in a0-plugin-argus records `a0-plugins#572` as open.
- Dependencies: owner sign-off of the new Patchbay thumbnails (this PR). One plugin per PR.
- **Difficulty**: easy. **Feasibility**: maintainer review; PRs failing 7+ days may be closed.
- **Simpler alternative**: none; this is the point of the repo.

### U4. Plan hygiene
- Status: Next. Evidence: `docs/plans/2026-09-05---a0-plugins-ui-ux-overhaul.md` plans work on `plugins/` directories that #8 removed; `2026-09-22-001-openrouter-spend-ci-plan.md` U1 to U4 are delivered (#7, #8, #9).
- **Difficulty**: easy. **Simpler alternative**: delete the 2026-09-05 plan (git history keeps it).

### U5. Archive
- Status: Later. Evidence: once cards are merged upstream, `index/` is a copy of upstream's `plugins/<name>/`.
- **Difficulty**: easy; archiving is a settings change, an owner action.
- **Feasibility**: none, except new plugins would need a new staging place (use a branch on the `a0-plugins` fork).
- **Simpler alternative**: stage in branches on `duketopceo/a0-plugins` from the start and retire this repo now.

## Verdict

Keep for now, archive after U3. Biggest simplification: the whole repo, once U3 lands.
