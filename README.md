# Agent Zero Plugins

Two independent [Agent Zero](https://github.com/agent0ai/agent-zero) plugins for `/a0/usr/plugins/`.

| Plugin | Purpose |
|--------|---------|
| `kurultai_people` | Search Kurultai for people and internal knowledge |
| `openrouter_usage` | OpenRouter org spend dashboard (management key) |

## Install

Copy each plugin folder into your Agent Zero persistent volume:

```bash
cp -r plugins/kurultai_people /a0/usr/plugins/
cp -r plugins/openrouter_usage /a0/usr/plugins/
```

Restart Agent Zero, open **Plugins**, enable each plugin, then configure in **Settings**.

### Secrets (`/a0/usr/secrets.env`)

| Key | Plugin | Required |
|-----|--------|----------|
| `KURULTAI_API_KEY` | kurultai_people | Optional (Bearer token when Kurultai requires auth) |
| `OPENROUTER_MANAGEMENT_KEY` | openrouter_usage | Required for usage data |

### kurultai_people

Settings → **External**: set `kurultai_base_url` (e.g. `http://127.0.0.1:8421`).

Optional: `kurultai_mcp_url` (e.g. `http://127.0.0.1:8421/mcp`) to prefer MCP over HTTP search.

### openrouter_usage

Settings → **Developer**: pick watched API keys, set aliases (`821713b8=luke`), refresh interval.

## Plugin Index

See `index/` for `agent0ai/a0-plugins` submission manifests (one repo per plugin at publish time).

## Layout

```
plugins/
├── kurultai_people/
└── openrouter_usage/
```
