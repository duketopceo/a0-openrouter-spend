from helpers.tool import Response, Tool
from usr.plugins.kurultai_people.helpers.client import kurultai_cite
from usr.plugins.kurultai_people.helpers.errors import friendly_error
from usr.plugins.kurultai_people.helpers.client import load_settings
from usr.plugins.kurultai_people.helpers.normalize import format_citation_for_agent


class KurultaiCite(Tool):
    async def execute(self, source="", source_id="", **kwargs):
        try:
            result = kurultai_cite(self.agent, str(source or ""), str(source_id or ""))
            message = format_citation_for_agent(result.get("citation"))
        except Exception as exc:
            settings = load_settings(self.agent)
            message = friendly_error(exc, settings.get("base_url", ""))
        return Response(message=message, break_loop=False)
