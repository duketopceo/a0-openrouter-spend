<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/wordmark-dark.svg">
    <img alt="a0-openrouter-spend" src="assets/brand/wordmark.svg" height="56">
  </picture>
</p>

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

Despite the repo name, this is not the OpenRouter spend plugin: that lives in
`openrouter_usage`. This repo only stages Plugin Hub cards. See
[ROADMAP.md](ROADMAP.md).

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

## Check locally

```bash
python -m pip install pyyaml
python3 scripts/validate_index.py   # exit 0 = every staged card passes the structural rules
```

## Contributing

Plugin behaviour changes belong in the standalone repo, never here (see
[AGENTS.md](AGENTS.md)). Design direction and brand assets (a proposal,
pending owner sign-off): [DESIGN.md](DESIGN.md), [assets/brand/](assets/brand/).
The staged `argus` and `omaseal` thumbnails use the Patchbay marks.

## License

MIT, see [LICENSE](LICENSE).
