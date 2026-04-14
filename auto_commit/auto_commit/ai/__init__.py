from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auto_commit.ai.base import AIProvider

PROVIDERS = {
    "openai": {
        "class": "OpenAIProvider",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "env_key": "OPENAI_API_KEY",
        "config_key": "openai",
        "docs_url": "https://platform.openai.com/api-keys",
    },
    "anthropic": {
        "class": "AnthropicProvider",
        "models": ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"],
        "env_key": "ANTHROPIC_API_KEY",
        "config_key": "anthropic",
        "docs_url": "https://console.anthropic.com/keys",
    },
    "gemini": {
        "class": "GeminiProvider",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro"],
        "env_key": "GEMINI_API_KEY",
        "config_key": "gemini",
        "docs_url": "https://aistudio.google.com/apikey",
    },
    "deepseek": {
        "class": "DeepSeekProvider",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "env_key": "DEEPSEEK_API_KEY",
        "config_key": "deepseek",
        "docs_url": "https://platform.deepseek.com/api_keys",
    },
    "grok": {
        "class": "GrokProvider",
        "models": ["grok-3", "grok-3-mini", "grok-2"],
        "env_key": "XAI_API_KEY",
        "config_key": "grok",
        "docs_url": "https://console.x.ai",
    },
    "mistral": {
        "class": "MistralProvider",
        "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest"],
        "env_key": "MISTRAL_API_KEY",
        "config_key": "mistral",
        "docs_url": "https://console.mistral.ai/api-keys",
    },
}

_PROVIDER_IMPORT_MAP: dict[str, tuple[str, str]] = {
    "OpenAIProvider": ("auto_commit.ai.openai_provider", "OpenAIProvider"),
    "AnthropicProvider": ("auto_commit.ai.anthropic_provider", "AnthropicProvider"),
    "GeminiProvider": ("auto_commit.ai.gemini_provider", "GeminiProvider"),
    "DeepSeekProvider": ("auto_commit.ai.deepseek_provider", "DeepSeekProvider"),
    "GrokProvider": ("auto_commit.ai.grok_provider", "GrokProvider"),
    "MistralProvider": ("auto_commit.ai.mistral_provider", "MistralProvider"),
}


def _resolve_provider_class(class_name: str):
    module_name, attr_name = _PROVIDER_IMPORT_MAP[class_name]
    module = import_module(module_name)
    return getattr(module, attr_name)


def create_provider(provider_name: str) -> "AIProvider":
    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}")
    class_name = PROVIDERS[provider_name]["class"]
    provider_cls = _resolve_provider_class(class_name)
    return provider_cls()


__all__ = ["PROVIDERS", "create_provider", "AIProvider"]
