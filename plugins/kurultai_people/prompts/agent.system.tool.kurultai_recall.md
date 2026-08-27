## kurultai_recall
Project-scoped memory recall from Kurultai. Use when the user refers to prior work in this agent/project namespace.
- `kurultai_recall`: args `query`, optional `project`, optional `limit`

example:
~~~json
{
  "thoughts": ["Recall project-scoped notes before answering."],
  "headline": "Recalling Kurultai memory",
  "tool_name": "kurultai_recall",
  "tool_args": { "query": "openrouter dashboard decisions" }
}
~~~
