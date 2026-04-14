from __future__ import annotations

import os

import pytest

from auto_commit.config import Config, load_config, save_config
from auto_commit.errors import ConfigNotFoundError


def test_config_save_and_load(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    config = Config(provider="openai", model="gpt-4o")

    save_config(config)
    loaded = load_config()

    assert loaded.provider == "openai"
    assert loaded.model == "gpt-4o"


def test_env_var_fallback(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "env-openai-key")

    config = Config(provider="openai", model="gpt-4o")
    config.api_keys["openai"] = ""
    save_config(config)

    loaded = load_config()
    assert loaded.effective_api_key("openai") == "env-openai-key"


def test_missing_config_raises_error(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))

    with pytest.raises(ConfigNotFoundError):
        load_config()
