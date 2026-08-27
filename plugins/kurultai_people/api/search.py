from helpers.api import ApiHandler, Input, Output, Request
from usr.plugins.kurultai_people.helpers.client import kurultai_search
from usr.plugins.kurultai_people.helpers.errors import friendly_error
from usr.plugins.kurultai_people.helpers.client import load_settings


class Search(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        query = str(input.get("query") or "")
        scope = str(input.get("scope") or "")
        source = str(input.get("source") or "").strip() or None
        limit = input.get("limit")
        try:
            context = self.use_context(str(input.get("context") or ""), create_if_not_exists=False)
            agent = context.agent0 if context else None
            parsed_limit = int(limit) if limit not in (None, "") else None
            return kurultai_search(agent, query, scope=scope, source=source, limit=parsed_limit)
        except Exception as exc:
            settings = load_settings(None)
            return {"ok": False, "error": friendly_error(exc, settings.get("base_url", "")), "hits": []}
