from helpers.extension import Extension
from helpers import plugins


class KurultaiFeatureCard(Extension):
    async def execute(self, banners: list | None = None, frontend_context: dict | None = None, **kwargs):
        if banners is None:
            return
        config = plugins.get_plugin_config("kurultai_people") or {}
        if str(config.get("kurultai_base_url") or config.get("kurultai_mcp_url") or "").strip():
            return
        banners.append(
            {
                "id": "kurultai_people-setup",
                "type": "feature",
                "priority": 40,
                "title": "Kurultai Memory",
                "description": "Search, recall, and cite your Kurultai brain from Agent Zero — excerpts with sources, not file dumps.",
                "thumbnail": "/plugins/kurultai_people/docs/logo.webp",
                "icon": "psychology",
                "cta_text": "Connect Kurultai",
                "cta_action": "open-plugin-config:kurultai_people",
                "dismissible": True,
            }
        )
