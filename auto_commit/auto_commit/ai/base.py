from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Final

import openai

if TYPE_CHECKING:
    from auto_commit.config import Config

SYSTEM_PROMPT: Final[str] = (
    "You are an expert developer. Analyze the git diff and return ONLY a conventional commit "
    "message following: (scope): Optional blank line + bullet-point body. "
    "Types: feat|fix|docs|style|refactor|test|chore|perf "
    "Max subject line: 72 chars. Language: match existing commit messages in diff, "
    "default English. No markdown, no code blocks. "
    "Prefer concise output. Use subject-only when possible. "
    "If body is needed, include at most 3 technical bullets, avoid marketing wording."
)


class AIProvider(ABC):
    @abstractmethod
    def generate(self, diff: str, config: Config) -> str:
        raise NotImplementedError


class OpenAICompatibleProvider(AIProvider):
    base_url: str | None = None

    def _client(self, config: Config) -> openai.OpenAI:
        key = config.effective_api_key(config.provider)
        kwargs: dict[str, str] = {"api_key": key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return openai.OpenAI(**kwargs)

    def generate(self, diff: str, config: Config) -> str:
        client = self._client(config)
        response = client.chat.completions.create(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": diff},
            ],
        )
        content = response.choices[0].message.content
        return (content or "").strip()
