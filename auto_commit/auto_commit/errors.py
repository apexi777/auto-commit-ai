from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.panel import Panel


class AutoCommitError(Exception):
    """Base error type for auto-commit."""


class AuthenticationError(AutoCommitError):
    pass


class RateLimitError(AutoCommitError):
    pass


class InsufficientFundsError(AutoCommitError):
    pass


class ContextLengthError(AutoCommitError):
    pass


class NetworkError(AutoCommitError):
    pass


class NoDiffError(AutoCommitError):
    pass


class GitNotFoundError(AutoCommitError):
    pass


class ConfigNotFoundError(AutoCommitError):
    pass


@dataclass
class ErrorContext:
    docs_url: Optional[str] = None


def _log_path() -> Path:
    return Path.home() / ".auto_commit" / "error.log"


def log_error(error: Exception) -> None:
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{datetime.now().isoformat()} {type(error).__name__}: {error}\n")


def map_provider_error(error: Exception, docs_url: str | None = None) -> AutoCommitError:
    text = str(error).lower()
    cls = type(error).__name__.lower()

    if "auth" in cls or "unauthorized" in text or "invalid api key" in text or "api key" in text and "invalid" in text:
        return AuthenticationError(f"Invalid API key. Get one at {docs_url}" if docs_url else "Invalid API key.")
    if "rate" in cls or "429" in text or "rate limit" in text or "too many requests" in text:
        return RateLimitError("Rate limit hit. Wait ~60s or switch model.")
    if "insufficient" in text or "credit" in text or "billing" in text or "payment" in text or "quota" in text:
        return InsufficientFundsError(
            f"Account out of credits. Top up at {docs_url}" if docs_url else "Account out of credits."
        )
    if "context" in text or "token" in text and "max" in text:
        return ContextLengthError("Diff too large even after chunking.")
    if "network" in cls or "connection" in text or "timed out" in text or "dns" in text:
        return NetworkError("No internet or API unreachable.")
    return AutoCommitError(str(error))


def render_error(error: Exception, docs_url: str | None = None) -> Panel:
    context = ErrorContext(docs_url=docs_url)
    mapped = error
    if not isinstance(error, AutoCommitError):
        mapped = map_provider_error(error, docs_url=context.docs_url)

    match mapped:
        case AuthenticationError():
            message = f"Invalid API key. Get one at {context.docs_url}" if context.docs_url else "Invalid API key."
        case RateLimitError():
            message = "Rate limit hit. Wait ~60s or switch model."
        case InsufficientFundsError():
            message = (
                f"Account out of credits. Top up at {context.docs_url}"
                if context.docs_url
                else "Account out of credits."
            )
        case ContextLengthError():
            message = "Diff too large even after chunking."
        case NetworkError():
            message = "No internet or API unreachable."
        case NoDiffError():
            message = "No staged changes. Run git add first."
        case GitNotFoundError():
            message = "Git not found. Install git first."
        case ConfigNotFoundError():
            message = "No config. Run: auto-commit config"
        case _:
            message = str(mapped)

    return Panel(message, title="Error", border_style="red")
