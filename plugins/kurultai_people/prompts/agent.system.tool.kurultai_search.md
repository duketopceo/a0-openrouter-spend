## kurultai_search
Hybrid search across the Kurultai brain. Returns excerpt-sized hits with citations — never full files.
- `kurultai_search`: args `query`, optional `scope` (`people` | `memory`), optional `source`, optional `limit`
- Prefer this for general knowledge and people lookups

example:
~~~json
{
  "thoughts": ["Search the Kurultai brain for grounded context."],
  "headline": "Searching Kurultai",
  "tool_name": "kurultai_search",
  "tool_args": { "query": "database migration notes", "scope": "memory" }
}
~~~
