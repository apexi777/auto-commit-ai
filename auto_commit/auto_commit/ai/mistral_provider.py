from __future__ import annotations

from auto_commit.ai.base import OpenAICompatibleProvider


class MistralProvider(OpenAICompatibleProvider):
    base_url = "https://api.mistral.ai/v1"
