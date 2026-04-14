from __future__ import annotations

from auto_commit.ai.base import OpenAICompatibleProvider


class GrokProvider(OpenAICompatibleProvider):
    base_url = "https://api.x.ai/v1"
