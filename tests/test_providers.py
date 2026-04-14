from __future__ import annotations

from types import SimpleNamespace

from auto_commit.ai.deepseek_provider import DeepSeekProvider
from auto_commit.ai.gemini_provider import GeminiProvider
from auto_commit.ai.grok_provider import GrokProvider
from auto_commit.ai.mistral_provider import MistralProvider
from auto_commit.ai.openai_provider import OpenAIProvider
from auto_commit.config import Config
from auto_commit.errors import AuthenticationError, InsufficientFundsError, RateLimitError, map_provider_error


def _config(provider: str) -> Config:
    cfg = Config(provider=provider, model="test-model")
    cfg.api_keys[provider] = f"{provider}-key"
    return cfg


def test_openai_returns_message(monkeypatch) -> None:
    class FakeClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return SimpleNamespace(
                        choices=[SimpleNamespace(message=SimpleNamespace(content="feat(cli): add command"))]
                    )

    monkeypatch.setattr("openai.OpenAI", lambda **kwargs: FakeClient())

    provider = OpenAIProvider()
    message = provider.generate("diff", _config("openai"))

    assert message == "feat(cli): add command"


def test_gemini_returns_message(monkeypatch) -> None:
    class FakeModels:
        @staticmethod
        def generate_content(**kwargs):
            return SimpleNamespace(text="fix(api): handle retries")

    class FakeClient:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.models = FakeModels()

    class FakeTypes:
        class GenerateContentConfig:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

    monkeypatch.setattr("google.genai.Client", FakeClient)
    monkeypatch.setattr("google.genai.types.GenerateContentConfig", FakeTypes.GenerateContentConfig)

    provider = GeminiProvider()
    message = provider.generate("diff", _config("gemini"))

    assert message == "fix(api): handle retries"


def test_deepseek_uses_openai_sdk_with_custom_base_url(monkeypatch) -> None:
    called = {}

    class FakeClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    def fake_openai(**kwargs):
        called.update(kwargs)
        return FakeClient()

    monkeypatch.setattr("openai.OpenAI", fake_openai)

    DeepSeekProvider().generate("diff", _config("deepseek"))
    assert called["base_url"] == "https://api.deepseek.com/v1"


def test_grok_uses_openai_sdk_with_custom_base_url(monkeypatch) -> None:
    called = {}

    class FakeClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    def fake_openai(**kwargs):
        called.update(kwargs)
        return FakeClient()

    monkeypatch.setattr("openai.OpenAI", fake_openai)

    GrokProvider().generate("diff", _config("grok"))
    assert called["base_url"] == "https://api.x.ai/v1"


def test_mistral_uses_openai_sdk_with_custom_base_url(monkeypatch) -> None:
    called = {}

    class FakeClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    def fake_openai(**kwargs):
        called.update(kwargs)
        return FakeClient()

    monkeypatch.setattr("openai.OpenAI", fake_openai)

    MistralProvider().generate("diff", _config("mistral"))
    assert called["base_url"] == "https://api.mistral.ai/v1"


def test_anthropic_auth_error_mapped() -> None:
    err = map_provider_error(Exception("401 invalid api key"), docs_url="https://console.anthropic.com/keys")
    assert isinstance(err, AuthenticationError)


def test_rate_limit_mapped() -> None:
    err = map_provider_error(Exception("429 rate limit"))
    assert isinstance(err, RateLimitError)


def test_insufficient_funds_mapped() -> None:
    err = map_provider_error(Exception("insufficient credits"), docs_url="https://billing.example")
    assert isinstance(err, InsufficientFundsError)
