from helpers.api import ApiHandler, Input, Output, Request
from usr.plugins.kurultai_people.helpers.client import load_settings, test_connection
from usr.plugins.kurultai_people.helpers.errors import friendly_error


class TestConnection(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        try:
            context = self.use_context(str(input.get("context") or ""), create_if_not_exists=False)
            agent = context.agent0 if context else None
            return test_connection(agent)
        except Exception as exc:
            settings = load_settings(None)
            return {"ok": False, "error": friendly_error(exc, settings.get("base_url", ""))}
