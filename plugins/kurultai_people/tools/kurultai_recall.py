from helpers.tool import Response, Tool
from usr.plugins.kurultai_people.helpers.client import kurultai_recall, load_settings
from usr.plugins.kurultai_people.helpers.errors import friendly_error
from usr.plugins.kurultai_people.helpers.normalize import format_hits_for_agent


class KurultaiRecall(Tool):
    async def execute(self, query="", project="", limit="", **kwargs):
        try:
            parsed_limit = int(limit) if str(limit).strip() else None
        except ValueError:
            parsed_limit = None
        try:
            result = kurultai_recall(
                self.agent,
                str(query or ""),
                project=str(project or ""),
                limit=parsed_limit,
            )
            hits = result.get("hits") or []
            header = f"Kurultai recall (project: {result.get('project', 'default')})"
            message = f"{header}\n\n{format_hits_for_agent(hits)}"
        except Exception as exc:
            settings = load_settings(self.agent)
            message = friendly_error(exc, settings.get("base_url", ""))
        return Response(message=message, break_loop=False)
