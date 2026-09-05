# Plan — Agent Zero plugins UI/UX overhaul (openrouter_usage + kurultai_people)

- **Date:** 2026-09-05
- **Repo:** `a0-openrouter-spend` (authoring monorepo for both Agent Zero plugins)
- **Request:** "Agent Zero both plugins need a complete UI/UX overhaul — forget what's there, take it next level."
- **Mode:** LFG pipeline (plan → work → simplify → review → ship).

## 1. Problem frame

Both plugins ship functional but minimal, hand-styled UIs. `plugins/kurultai_people` is a single search modal + settings page. `plugins/openrouter_usage` in this repo is a stale pre-"ultimate" copy (no workspaces, no analytics tabs, no ORI) while `duketopceo/openrouter_usage@main` already carries the workspace-aware backend. Goal: a cohesive, "next level" UI across both plugins — shared design language, real information hierarchy, loading/empty/error/stale states, responsive and touch-safe, within Agent Zero's Alpine.js modal/store conventions.

## 2. Settled decisions

| Decision | Class | Rejected alternative | Reason |
|---|---|---|---|
| Both plugins in `a0-openrouter-spend` are in scope (`openrouter_usage` + `kurultai_people`) | user-directed | one plugin only | "both plugins" |
| Discard current UI layout and rebuild, keep Agent Zero wiring (`createStore`, `callJsonApi`, `openModal`, toasts, `x-data`) | user-directed | incremental polish | "forget what's there" |
| Sync `plugins/openrouter_usage` to `duketopceo/openrouter_usage@main` as the backend baseline before UI work | user-approved (derived) | overhaul UI on the stale backend | monorepo copy predates workspaces/analytics/ORI; diverging further is worse |
| Shared design system duplicated per plugin (`ui-kit.css` per plugin), not a cross-plugin shared asset | user-approved (derived) | shared file outside plugin dirs | plugins must stay self-contained for `cp -r` install |
| Management key stays server-side; nothing secret-bearing in JS/HTML/payloads | user-approved | — | standing constraint |
| ORI apply stays behind explicit confirmation, now an in-page confirm dialog instead of `window.confirm` | user-approved | keep `confirm()` | polish + CodeRabbit-era UX |

## 3. Scope

**In:** all user-facing surfaces — dashboard modals, config pages, sidebar quick-action widgets, search modal; shared styling; frontend state rework (race guards, stale handling, persisted view/tab/workspace).

**Out:** backend API contracts (already shipped), new endpoints, plugin.yaml schema changes, marketplace thumbnails, upstream `agent0ai/a0-plugins` submission, `lukedaduke.nexus` (untracked, unrelated), dayflow.

## 4. Design system (new, per-plugin duplicated)

`webui/ui-kit.css` — tokens + components:

- Tokens: `--ui-bg`, `--ui-surface`, `--ui-surface-2`, `--ui-border`, `--ui-text`, `--ui-text-dim`, `--ui-accent`, `--ui-good`, `--ui-warn`, `--ui-bad`, radii, spacing scale, shadows. All with `var(--color-…)` fallbacks so it follows Agent Zero theming where present.
- Components: `.ui-hero` (logo + title + status pill), `.ui-kpi` cards, `.ui-seg` segmented control, `.ui-table` (sticky header, scrollable), `.ui-bar`/`ui-spark` CSS bars, `.ui-banner` (warn/error/stale), `.ui-skeleton`, `.ui-empty`, `.ui-chip`, `.ui-dialog` (in-page confirm), `.ui-field`.
- One breakpoint: `720px`; ≥44px touch targets; `[x-cloak]` rule; reduced-motion support.

`webui/ui.js` — tiny shared helpers: `fmtUsd`, `fmtNum`, `relTime`, `sparkMax`, `barPct`, `escHtml` (for any interpolated text).

## 5. Implementation units

| ID | Unit | Files | Depends |
|----|------|-------|---------|
| U0 | Sync `plugins/openrouter_usage` to `duketopceo/openrouter_usage@main` (engine/, api/, helpers/, tests/, default_config.yaml, plugin.yaml, README, webui as baseline) | `plugins/openrouter_usage/**` | — |
| U1 | UI kit per plugin | `plugins/{openrouter_usage,kurultai_people}/webui/ui-kit.css`, `webui/ui.js` | U0 |
| U2 | `openrouter_usage` store rework: request sequence guards, stale flag surface, persisted view/tab/workspace, per-tab fetch dispatch incl. onOpen restore, workspace-switch invalidates tab data, `formatUsd` NaN-safe, month math by real dates not `M/D` labels | `plugins/openrouter_usage/webui/usage-store.js` | U0, U1 |
| U3 | `openrouter_usage` dashboard rebuild: hero (logo, workspace pill-select, refresh, view seg), KPI strip (spend, balance, burn, top model/key, workspace), tab rail (overview/spend/models/providers/apps/keys/workspaces/activity/budgets/ORI), scrollable sticky tables, ORI diff cards + in-page confirm, alerts/banners, skeletons | `plugins/openrouter_usage/webui/usage-dashboard.html` | U1, U2 |
| U4 | `openrouter_usage` config + sidebar widget: grouped sections w/ descriptions, pinned workspace select, connection state; widget shows spend + stale dot + mini sparkline | `plugins/openrouter_usage/webui/config.html`, `plugins/openrouter_usage/extensions/webui/sidebar-quick-actions-main-end/usage-widget.html` | U1, U2 |
| U5 | `kurultai_people` store rework: recent searches (localStorage ≤10), filters (source, project override, limit), result actions (copy cite, open source link if URL), seq-guarded search, empty/error/loading states | `plugins/kurultai_people/webui/kurultai-store.js` | U1 |
| U6 | `kurultai_people` search modal rebuild: hero, large query field (autofocus, Enter), filter row, result cards (title, snippet, score bar, source chip), "who knows" rail, skeletons, recents chips | `plugins/kurultai_people/webui/search-modal.html` | U1, U5 |
| U7 | `kurultai_people` config + sidebar button: hero + connection card with live test status pill, grouped fields, hint text; sidebar button keeps logo, gains tooltip state | `plugins/kurultai_people/webui/config.html`, `plugins/kurultai_people/extensions/webui/sidebar-quick-actions-main-end/kurultai-search.html` | U1, U5 |
| U8 | Metadata/docs: bump both `plugin.yaml` versions, refresh README UI notes | `plugins/*/plugin.yaml`, `plugins/*/README.md`, `README.md` | U3, U6 |

## 6. Requirements → units

| Requirement | Units |
|---|---|
| Complete UI/UX overhaul, both plugins | U1–U8 |
| Keep Agent Zero Alpine/store/modal conventions | U2–U7 |
| Self-contained plugins | U0, U1 |
| Workspaces/analytics/ORI available in UI | U0, U2, U3 |
| No secrets client-side | all |
| Loading/empty/error/stale states everywhere | U2–U7 |
| Explicit confirm before ORI apply | U3 |

## 7. Test scenarios

- **Happy:** dashboard renders KPIs + all tabs; workspace switch refetches; ORI preview → confirm → apply; kurultai search returns cards + who-knows; recent searches persist.
- **Edge:** zero workspaces; empty hits; `NaN`/null metrics; 90+ day history across year boundary; duplicate tab clicks mid-flight (seq guard); narrow viewport.
- **Error:** missing `OPENROUTER_MANAGEMENT_KEY` → empty state; API `ok:false` → banner, stale data kept; kurultai unreachable → error state + config CTA.
- **Integration:** sidebar widget label/stale dot; modal open/close cleanup (poll stop); config page field round-trip.
- **Unit (existing + new):** keep `plugins/openrouter_usage/tests/` suite green after U0 sync; no new backend logic → no new unit tests required; store helpers covered where pure.

## 8. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Agent Zero CSS vars differ across versions | tokens layered over `var(--color-…)` fallbacks; neutral defaults |
| Alpine `x-for`/`x-if` pitfalls (keys, hidden-eval) | stable `:key` on real ids/hashes; `x-if` not `x-show` for heavy panels |
| Monorepo vs standalone `openrouter_usage` divergence | U0 sync first; note in plan + README that monorepo is canonical for dev, standalone is publish mirror |
| No live Agent Zero instance here | static-serve HTML sanity check + manual checklist; browser test via BrowserOS if a0 running |
| `index/` thumbnails/logo paths must stay | don't touch `docs/logo.webp`, `index/` |

## 9. Verification

`python -m unittest discover` in `plugins/openrouter_usage/tests`, `py_compile` all py files, serve webui HTML statically for a visual smoke, diff review, then PR.
