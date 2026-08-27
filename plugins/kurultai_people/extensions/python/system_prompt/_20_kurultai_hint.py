from helpers.extension import Extension
from agent import LoopData


class KurultaiHint(Extension):
    async def execute(self, system_prompt: list[str] | None = None, loop_data: LoopData = LoopData(), **kwargs):
        if system_prompt is None:
            return
        system_prompt.append(
            "For questions about people, roles, teams, or indexed internal documents, "
            "call kurultai_search before guessing. Do not invent employee names or contact details."
        )
