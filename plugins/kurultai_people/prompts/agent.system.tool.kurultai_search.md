## kurultai_search
Use for org/people/internal-doc questions before guessing.
- `kurultai_search`: args `query`, optional `scope` (`people`), optional `source`, optional `limit`
- Returns excerpt-sized hits with source citations from Kurultai

example:
~~~json
{
  "thoughts": ["I should search Kurultai for this person."],
  "headline": "Searching Kurultai",
  "tool_name": "kurultai_search",
  "tool_args": {
    "query": "Luke Duke role",
    "scope": "people"
  }
}
~~~
