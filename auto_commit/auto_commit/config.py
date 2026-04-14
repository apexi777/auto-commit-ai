from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import questionary
from rich.console import Console
from rich.panel import Panel

from auto_commit.ai import PROVIDERS
from auto_commit.errors import ConfigNotFoundError


@dataclass
class Config:
    provider: str = "anthropic"
    model: str = "claude-sonnet-4-5"
    api_keys: dict[str, str] = field(
        default_factory=lambda: {
            "openai": "",
            "anthropic": "",
            "gemini": "",
            "deepseek": "",
            "grok": "",
            "mistral": "",
        }
    )
    language: str = "auto"
    max_tokens: int = 512
    temperature: float = 0.3

    def effective_api_key(self, provider: str | None = None) -> str:
        key = provider or self.provider
        configured = self.api_keys.get(key, "")
        if configured:
            return configured

        provider_meta = PROVIDERS[key]
        env_name = provider_meta["env_key"]
        return os.getenv(env_name, "")


def config_path() -> Path:
    return Path.home() / ".auto_commit" / "config.json"


def load_config() -> Config:
    path = config_path()
    if not path.exists():
        raise ConfigNotFoundError("Config file not found")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Config(**payload)


def save_config(config: Config) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(config), indent=2) + "\n", encoding="utf-8")


def _last4(masked: str) -> str:
    if len(masked) < 4:
        return "****"
    return f"****{masked[-4:]}"


def show_config(console: Console, config: Config) -> None:
    safe_config: dict[str, Any] = asdict(config)
    safe_config["api_keys"] = {
        key: (_last4(value) if value else "(env or unset)") for key, value in config.api_keys.items()
    }
    pretty = json.dumps(safe_config, indent=2)
    console.print(Panel(pretty, title="Current Config", border_style="cyan"))


def configure_interactive(console: Console) -> Config:
    try:
        current = load_config()
    except ConfigNotFoundError:
        current = Config()

    provider_choices = list(PROVIDERS.keys())
    provider = questionary.select(
        "Select provider", choices=provider_choices, default=current.provider
    ).ask()
    if not provider:
        return current

    model_choices = PROVIDERS[provider]["models"]
    default_model = current.model if current.provider == provider and current.model in model_choices else model_choices[0]
    model = questionary.select("Select model", choices=model_choices, default=default_model).ask()
    if not model:
        return current

    current_key = current.api_keys.get(provider, "")
    suffix = f" (currently {_last4(current_key)})" if current_key else ""
    api_key = questionary.password(f"Enter API key for {provider}{suffix}").ask()
    if api_key is None:
        return current

    updated = Config(
        provider=provider,
        model=model,
        api_keys=dict(current.api_keys),
        language=current.language,
        max_tokens=current.max_tokens,
        temperature=current.temperature,
    )
    if api_key.strip():
        updated.api_keys[provider] = api_key.strip()

    save_config(updated)
    console.print(Panel("Configuration saved.", title="Success", border_style="green"))
    return updated
