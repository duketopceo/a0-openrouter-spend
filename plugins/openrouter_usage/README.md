# OpenRouter Usage

Minimal OpenRouter org spend widget for Agent Zero.

## Install

1. Copy this folder to `/a0/usr/plugins/openrouter_usage/`
2. Restart Agent Zero and enable the plugin
3. Add `OPENROUTER_MANAGEMENT_KEY` to Agent Zero Secrets (org **management** key, not an inference key)
4. Settings → **Developer** → fetch keys, select watched keys, set aliases

## API (server-side only)

- `GET /v1/credits`
- `GET /v1/keys`
- `GET /v1/activity?api_key_hash=<prefix>` per watched key

Overview is cached (default 5 minutes). Widget polls on the configured interval.

## Manual test

- [ ] Missing management key → empty state copy in widget
- [ ] With key → widget shows 30-day spend and credit balance
- [ ] Detailed view charts and table populate
- [ ] One key activity failure → partial data + `last_error`
- [ ] Management key never appears in browser network responses

## License

MIT
