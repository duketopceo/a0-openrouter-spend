<p align="center">
  <img src="docs/logo.webp" alt="Kurultai Memory" width="120" />
</p>

# Kurultai Memory

**Connect Agent Zero to your [Kurultai](https://github.com/duketopceo/kurultai) brain.**

Search, recall, and cite indexed knowledge with excerpt-sized results and source paths — never whole-file dumps into context.

---

## Why

Kurultai indexes notes, chats, code, and connectors into one hybrid FTS + vector store. This plugin wires that brain into Agent Zero as first-class tools the agent can call when users ask about people, prior decisions, or internal docs.

| Tool | When to use |
|------|-------------|
| `kurultai_search` | General hybrid search; auto-routes people & memory queries |
| `kurultai_recall` | Project-scoped agent memory (`/api/recall`) |
| `kurultai_cite` | One grounded excerpt when you know `source` + `source_id` |

---

## Install

```bash
cp -r kurultai_people /a0/usr/plugins/
```

Restart Agent Zero → **Plugins** → enable **Kurultai Memory**.

### 1. Secrets (optional)

`/a0/usr/secrets.env`

```env
KURULTAI_API_KEY=your-bearer-token
```

### 2. Settings → External

| Field | Example |
|-------|---------|
| Base URL | `http://127.0.0.1:8421` |
| MCP URL | `http://127.0.0.1:8421/mcp` (optional) |
| Project | `default` or your `KURULTAI_PROJECT` |

Click **Test connection**.

---

## Kurultai daemon

```bash
kurultai daemon --port 8421
```

HTTP routes used:

- `GET/POST /api/search`
- `POST /api/recall`
- `POST /cite`
- `POST /who_knows`

---

## Agent tools

```json
{
  "tool_name": "kurultai_recall",
  "tool_args": { "query": "what did we decide about openrouter keys" }
}
```

Memory-style queries automatically prefer recall when **Prefer project recall** is enabled.

---

## Manual checklist

- [ ] Test connection returns sample hits
- [ ] `kurultai_search` answers a people question with citations
- [ ] `kurultai_recall` returns project-scoped excerpts
- [ ] No secrets committed to git

---

## License

MIT
