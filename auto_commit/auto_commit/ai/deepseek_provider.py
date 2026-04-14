from __future__ import annotations

from auto_commit.ai.base import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):
    base_url = "https://api.deepseek.com/v1"
