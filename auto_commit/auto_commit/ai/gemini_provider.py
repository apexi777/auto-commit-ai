from __future__ import annotations

from typing import TYPE_CHECKING

from auto_commit.ai.base import AIProvider, SYSTEM_PROMPT

if TYPE_CHECKING:
    from auto_commit.config import Config


class GeminiProvider(AIProvider):
    def generate(self, diff: str, config: Config) -> str:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=config.effective_api_key("gemini"))
        prompt = f"{SYSTEM_PROMPT}\n\n{diff}"
        response = client.models.generate_content(
            model=config.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=config.max_tokens,
                temperature=config.temperature,
            ),
        )
        return (response.text or "").strip()
