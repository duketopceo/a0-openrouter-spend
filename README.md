# Agent Zero Plugins

<p align="center">
  <img src="plugins/kurultai_people/docs/logo.webp" width="72" alt="Kurultai Memory" />
  <img src="plugins/openrouter_usage/docs/logo.webp" width="72" alt="OpenRouter Usage" />
</p>

Two independent plugins for [Agent Zero](https://github.com/agent0ai/agent-zero) v2.8+.

| Plugin | One-liner |
|--------|-----------|
| [**Kurultai Memory**](plugins/kurultai_people/) | Search, recall, and cite your [Kurultai](https://github.com/duketopceo/kurultai) brain |
| [**OpenRouter Usage**](plugins/openrouter_usage/) | Org spend widget + dashboard via management key |

## Quick install

```bash
cp -r plugins/kurultai_people /a0/usr/plugins/
cp -r plugins/openrouter_usage /a0/usr/plugins/
```

Restart → **Plugins** → enable both.

### Secrets (`/a0/usr/secrets.env`)

```env
KURULTAI_API_KEY=...              # optional
OPENROUTER_MANAGEMENT_KEY=...     # required for usage widget
```

## Plugin Hub / Store

Each plugin includes:

- `docs/logo.webp` — store thumbnail & welcome card art
- `index/<name>/index.yaml` — manifest for [agent0ai/a0-plugins](https://github.com/agent0ai/a0-plugins)
- Discovery **feature cards** when not yet configured

## Docs

- [Kurultai Memory README](plugins/kurultai_people/README.md)
- [OpenRouter Usage README](plugins/openrouter_usage/README.md)
