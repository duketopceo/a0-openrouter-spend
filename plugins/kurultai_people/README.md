# Kurultai People

Agent Zero plugin for [Kurultai](https://github.com/duketopceo/kurultai) search — people, roles, and indexed knowledge.

## Install

1. Copy this folder to `/a0/usr/plugins/kurultai_people/`
2. Restart Agent Zero and enable the plugin
3. Settings → **External** → set `kurultai_base_url`
4. Optional: add `KURULTAI_API_KEY` to Agent Zero Secrets (Bearer token)

## Kurultai daemon

Run Kurultai with HTTP enabled:

```bash
kurultai daemon --port 8421
```

Plugin uses:

- `GET/POST /api/search`
- `POST /who_knows` (person-related queries)
- Optional `POST /mcp` when `kurultai_mcp_url` is set

## Agent tool

`kurultai_search` — args: `query`, optional `scope=people`, `source`, `limit`.

## Manual test

- [ ] Settings test connection returns sample hits
- [ ] Agent answers "who is …" using `kurultai_search`
- [ ] Unreachable host shows toast error, not a stack trace
- [ ] No API key in plugin config files

## License

MIT
