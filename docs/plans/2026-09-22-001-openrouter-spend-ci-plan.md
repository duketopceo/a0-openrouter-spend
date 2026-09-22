# Plan: a0-openrouter-spend → 10/10

**Date:** 2026-09-22 · **Status:** proposed · **Depth:** lightweight
**Origin:** repo scorecard pass — engineering rigor 7, docs 5, focus 5.

## Problem frame

This repo bundles two Agent Zero plugins (`kurultai_people`, `openrouter_usage`) plus an
`index/` of plugin metadata. It **already has tests — but no CI runs them**, so they can
rot silently. It also already has a plan doc (`docs/plans/2026-09-05-…-ui-ux-overhaul.md`)
and `docs/PUBLISHING.md`. And there is a real open question: the `kurultai_people`
plugin also lives in the standalone `duketopceo/kurultai_people` repo (which just got a
hardening plan in PR #2) — two copies of one plugin with no documented source of truth.

## Scope

**In:** CI for the existing tests, source-of-truth decision, index validation,
publishing-docs verification.
**Out:** new plugins, UI/UX overhaul work (already planned separately), changes to the
standalone `kurultai_people` repo.

## Implementation units

### U1 — CI for existing tests
**Files:** `.github/workflows/ci.yml` (new)
- Run `pytest` on push + PR (match the Python versions the plugins target).
**Test scenarios:** n/a (workflow config) — verify with a trivial PR; the existing
suite must pass unmodified, or fix what it catches.

### U2 — Source-of-truth decision
**Files:** `README.md` or `docs/SOURCE_OF_TRUTH.md` (new)
- Decide and record: is the standalone `kurultai_people` repo canonical (and this
  repo's `plugins/kurultai_people/` a synced copy), or the reverse? Pick a sync
  direction or a single home; delete or submodule the other.
**Test scenarios:** n/a — the decision is the deliverable; implementation follows.

### U3 — Index validation
**Files:** `tests/test_index.py` (new) or extend CI
- Check `index/*/index.yaml` matches the corresponding `plugins/*/plugin.yaml`
  (name, version) so the catalog can't drift from the plugins.
**Test scenarios:** bump a plugin version without updating the index → test fails.

### U4 — Publishing docs verification
**Files:** `docs/PUBLISHING.md` (verify)
- Walk the publishing steps verbatim; fix what is stale.
**Test scenarios:** n/a — review criterion: the steps work as written.

## Key decisions

- U2 (the duplication decision) comes **before** further plugin edits — no more changes
  to two copies in parallel.
- CI runs the tests that already exist; writing new tests is out of scope here.

## Assumptions / open questions

- Is this repo the staging area for the a0-plugins index? If yes, say so in the README —
  it explains the repo's purpose to visitors.
- The UI/UX overhaul plan (2026-09-05) is separate work; this plan doesn't duplicate it.
