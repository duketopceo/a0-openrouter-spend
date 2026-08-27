from helpers.extension import Extension
from agent import LoopData


class KurultaiHint(Extension):
    async def execute(self, system_prompt: list[str] | None = None, loop_data: LoopData = LoopData(), **kwargs):
        if system_prompt is None:
            return
        system_prompt.append(
            "Kurultai is your indexed knowledge brain. For people, org, or internal-doc questions, "
            "call kurultai_search before guessing. For project-scoped prior work, prefer kurultai_recall. "
            "To pin one source, use kurultai_cite. Never invent employee names or contact details."
        )
