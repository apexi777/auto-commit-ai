from __future__ import annotations

from typing import TYPE_CHECKING

import anthropic

from auto_commit.ai.base import AIProvider, SYSTEM_PROMPT

if TYPE_CHECKING:
    from auto_commit.config import Config


class AnthropicProvider(AIProvider):
    def generate(self, diff: str, config: Config) -> str:
        client = anthropic.Anthropic(api_key=config.effective_api_key("anthropic"))
        message = client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": diff}],
        )
        parts = []
        for chunk in message.content:
            text = getattr(chunk, "text", "")
            if text:
                parts.append(text)
        return "\n".join(parts).strip()
