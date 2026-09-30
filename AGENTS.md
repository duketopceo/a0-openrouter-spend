# AGENTS.md — Agent Zero Plugins (dev monorepo)

Read this before changing anything here. Two facts below cause most of the
damage an agent can do to this repo, and both are silent when you get them
wrong.

## This is the dev monorepo, not the shipped plugin

`docs/PUBLISHING.md` defines the topology:

| What | Where |
|------|-------|
| **Dev monorepo** (this repo) | `plugins/kurultai_people/`, `plugins/openrouter_usage/` |
| **Public plugin repo** (one per plugin) | GitHub repo root = plugin files |
| **Index entry** | PR to `agent0ai/a0-plugins` adding `plugins/<name>/index.yaml` |

Agent Zero clones the **standalone** repo into `/a0/usr/plugins/<name>/` on
install. A change made only to `plugins/<name>/` in this repo does not reach a
single user.

- For `openrouter_usage`, which has a standalone repo: make the change in
  `duketopceo/openrouter_usage`.
- For `kurultai_people`, which does **not** have one yet: this monorepo *is* the
  source of truth, so make the change in `plugins/kurultai_people/`.

### `plugins/openrouter_usage/` here is a stale copy, and it has drifted

As of `b978764` (2026-09-11) the copy diverges from the shipped
`duketopceo/openrouter_usage` (head `0bbf3c9`, 2026-09-16). Verified with
`diff -rq` between the two working trees:

```
Only in ou-standalone: .github            # the standalone already has CI
Only in ou-standalone: .gitignore
Only in ou-standalone: CHANGELOG.md
Only in ou-standalone: docs
Files .../plugins/openrouter_usage/README.md       and .../openrouter_usage/README.md       differ
Files .../plugins/openrouter_usage/engine/db.py   and .../openrouter_usage/engine/db.py   differ
Files .../plugins/openrouter_usage/tests/test_engine.py and .../openrouter_usage/tests/test_engine.py differ
```

The `db.py` difference is the standalone's `fix(db): canonicalize timestamps
for correct lexical range/prune comparisons (#5)`. That fix is **not** in this
copy, and `engine/db.py` is where it lives.

Test counts differ accordingly, which is the cheapest drift detector:

| Tree | Command | Result |
|------|---------|--------|
| this repo, `plugins/openrouter_usage` | `python -m unittest discover -s tests -t .` | **26 tests** |
| standalone `openrouter_usage` | same command | **28 tests** |

**Do not "fix" the monorepo copy to match.** Syncing the two is a decision
about which direction is authoritative, and it is the owner's. Raise it.

`plugins/kurultai_people/` has no standalone repo yet and no test suite.

## Tests

There is exactly one suite, and it belongs to the `openrouter_usage` copy.

```bash
cd plugins/openrouter_usage
python -m unittest discover -s tests -t .
```

Verified green on CPython **3.11, 3.12, 3.13 and 3.14** (26 tests, ~0.3 s, no
network, no third-party packages — the suite is stdlib `unittest` only).

### `-t .` is load-bearing. Do not drop it.

```
$ python -m unittest discover -s tests
Ran 1 test in 0.000s
FAILED (errors=1)
```

`-s tests` alone sets the top-level directory to `tests/`, so
`import helpers...` and `import engine...` stop resolving. `-t .` keeps the
plugin root importable. This is the same constraint the standalone repo has,
and the reason its `AGENTS.md` carries the same warning.

`tests/__init__.py` is the other load-bearing file. It puts `tests/_site` on
`sys.path`, and `tests/_site/usr/plugins/openrouter_usage/__init__.py` is a
three-line shim:

```python
__path__ = [str(Path(__file__).resolve().parents[5])]
```

That points the `usr.plugins.openrouter_usage` package at the **real plugin
root**, so `engine/`, `helpers/` and everything else resolve from the plugin
tree itself. Verified by adding a new module under `engine/` with no mirror
under `tests/_site/` and importing it successfully.

**So do not mirror new modules into `tests/_site/`.** The shim exists precisely
so you do not have to, and copying files there creates duplicates that drift
from the originals. Add the module where it belongs, under the plugin.

`tests/fixtures/*.json` are checked-in API responses for `engine/`. They are
fixtures, not live data — do not "refresh" them from a real account.

## `api/test_connection.py` is a route, not a test

`plugins/kurultai_people/api/test_connection.py` looks like a test module. It is
not. It is an `ApiHandler` endpoint named `TestConnection` that Agent Zero
mounts, and it calls `test_connection(agent)` from `helpers/client.py` at
runtime. The `test_` prefix is a false positive for any
`discover -p 'test*.py'`. Nothing in this repo tests `kurultai_people`.

## Layout and invariants

```
plugins/<name>/
  plugin.yaml            # `name:` MUST equal the folder name
  api/*.py               # ApiHandler routes mounted by Agent Zero
  engine/                # openrouter_usage only: real logic + the test suite
  helpers/               # shared client, error, format, cache helpers
  extensions/python/     # banners + system-prompt injection
  extensions/webui/      # sidebar widgets, inlined into Agent Zero's UI
  tools/*.py             # agent-callable tools
  prompts/*.md           # tool system prompts
  webui/                 # styles, store, views
  tests/_site/           # import shim pointing at the plugin root — do not delete
index/<name>/            # Plugin Hub entry: index.yaml + thumbnail.webp
```

- Plugin code imports **as `usr.plugins.<name>.*`**, not relatively. That is
  the Agent Zero install path, not a stylistic choice. See `tests/_site/`.
- `plugins/openrouter_usage/` is the only plugin with an `engine/` package.
  `kurultai_people` puts its logic in `helpers/`. Do not unify them.
- `webui/ui-kit.css` and `webui/ui.js` are duplicated per plugin **on purpose**,
  because each plugin is copied into a separate A0 install directory. Sharing
  them across plugins would break standalone installs.
- The management key is read in `engine/` and in
  `helpers/openrouter_client.py`. The invariant that matters is
  **server-side vs browser-side**, not which file. Never move key handling
  into anything under `webui/`, which is served to the browser.
- `thumbnail.webp` must stay under 20 KB; the Hub rejects larger files.

## Publishing

`docs/PUBLISHING.md` is the procedure and it is current — follow it rather than
reconstructing it. Before PRing to `agent0ai/a0-plugins`, the `github:` field in
`index/<name>/index.yaml` must point at the standalone repo, and the plugin has
to have been run in a real Agent Zero install first.

## Not in this repo

- No build step, no package manager, no dependency manifest. The plugins are
  plain Python and are **copied**, not installed. Do not add a `pyproject.toml`
  or a `requirements.txt` to "fix" that; it would be a lie about how the code
  ships.
- No linter or formatter config.
- No `INDEX.md` and no `scripts/luke-index-watcher.py`. This repo is **not** part
  of the grounding-index family. Do not add one, and do not copy the watcher in
  from a sibling repo.
