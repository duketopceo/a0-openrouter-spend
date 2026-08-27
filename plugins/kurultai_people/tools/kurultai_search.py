from helpers.tool import Response, Tool
from usr.plugins.kurultai_people.helpers.client import kurultai_search
from usr.plugins.kurultai_people.helpers.errors import friendly_error
from usr.plugins.kurultai_people.helpers.normalize import format_hits_for_agent


class KurultaiSearch(Tool):
    async def execute(self, query="", scope="", source="", limit="", **kwargs):
        try:
            parsed_limit = int(limit) if str(limit).strip() else None
        except ValueError:
            parsed_limit = None
        try:
            result = kurultai_search(
                self.agent,
                str(query or ""),
                scope=str(scope or ""),
                source=str(source or "").strip() or None,
                limit=parsed_limit,
            )
        except Exception as exc:
            settings = {}
            try:
                from usr.plugins.kurultai_people.helpers.client import load_settings

                settings = load_settings(self.agent)
            except Exception:
                pass
            return Response(message=friendly_error(exc, settings.get("base_url", "")), break_loop=False)

        hits = result.get("hits") or []
        who_knows = result.get("who_knows") or []
        parts = [format_hits_for_agent(hits)]
        if who_knows:
            lines = ["Sources that may know about this topic:"]
            for row in who_knows:
                lines.append(f"- {row.get('source', 'unknown')} ({row.get('count', '?')} hits)")
            parts.append("\n".join(lines))
        return Response(message="\n\n".join(part for part in parts if part), break_loop=False)
