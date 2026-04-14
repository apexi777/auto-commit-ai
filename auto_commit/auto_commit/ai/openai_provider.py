from __future__ import annotations

from typing import TYPE_CHECKING

import openai

from auto_commit.ai.base import AIProvider, SYSTEM_PROMPT

if TYPE_CHECKING:
    from auto_commit.config import Config


class OpenAIProvider(AIProvider):
    def generate(self, diff: str, config: Config) -> str:
        client = openai.OpenAI(api_key=config.effective_api_key("openai"))
        response = client.chat.completions.create(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": diff},
            ],
        )
        return (response.choices[0].message.content or "").strip()
