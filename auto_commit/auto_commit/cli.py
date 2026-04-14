from __future__ import annotations

import base64
import os
import shutil
import subprocess
import sys
from typing import Iterable

import click
import pyperclip
import questionary
from rich.console import Console
from rich.panel import Panel

from auto_commit import __version__
from auto_commit.ai import PROVIDERS, create_provider
from auto_commit.config import configure_interactive, load_config, show_config
from auto_commit.errors import AutoCommitError, ContextLengthError, log_error, render_error
from auto_commit.git import MAX_DIFF_CHARS, chunk_diff_by_file_boundary, commit_message, get_staged_diff

console = Console()


def _clipboard_payload(text: str) -> str:
    """Return only commit subject text after first colon for clipboard copy."""
    first_line = text.strip().splitlines()[0] if text.strip() else ""
    head, sep, tail = first_line.partition(":")
    if not sep:
        return first_line.strip()
    return tail.lstrip().strip()


def _silent_pyperclip_copy(text: str) -> bool:
    """Copy with pyperclip while suppressing noisy backend stderr output."""
    try:
        payload = _clipboard_payload(text)
        saved_stderr_fd = os.dup(2)
        try:
            with open(os.devnull, "w", encoding="utf-8") as devnull:
                os.dup2(devnull.fileno(), 2)
                pyperclip.copy(payload)
                pasted = pyperclip.paste() or ""
        finally:
            os.dup2(saved_stderr_fd, 2)
            os.close(saved_stderr_fd)
        return pasted == payload
    except Exception:  # noqa: BLE001
        return False


def _clipboard_fallback_copy(text: str) -> bool:
    """Fallback to platform tools if pyperclip backend reports success incorrectly."""
    payload = _clipboard_payload(text)
    candidates: list[list[str]] = []
    if sys.platform == "darwin":
        candidates.append(["pbcopy"])
    elif os.name == "nt":
        candidates.append(["clip"])
    else:
        candidates.extend(
            [
                ["wl-copy"],
                ["xclip", "-selection", "clipboard"],
                ["xsel", "--clipboard", "--input"],
            ]
        )

    for cmd in candidates:
        if shutil.which(cmd[0]) is None:
            continue
        try:
            result = subprocess.run(cmd, input=payload, text=True, capture_output=True, check=False)
            if result.returncode == 0:
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _osc52_copy(text: str) -> bool:
    """Try terminal clipboard copy via OSC52 escape sequence."""
    try:
        payload = _clipboard_payload(text)
        encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        # OSC 52: set clipboard from terminal session.
        sys.stdout.write(f"\033]52;c;{encoded}\a")
        sys.stdout.flush()
        return True
    except Exception:  # noqa: BLE001
        return False


def _copy_to_clipboard(text: str) -> bool:
    if _silent_pyperclip_copy(text):
        return True
    if _clipboard_fallback_copy(text):
        return True
    return _osc52_copy(text)


def _clean_message(text: str) -> str:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _normalize_commit_message(text: str) -> str:
    cleaned = _clean_message(text)
    if not cleaned:
        return cleaned

    lines = cleaned.splitlines()
    subject = lines[0].strip()
    if not subject:
        return cleaned

    bullets: list[str] = []
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        bullet = stripped if stripped.startswith(("-", "*")) else f"- {stripped}"
        bullets.append(bullet)
        if len(bullets) == 3:
            break

    if not bullets:
        return subject
    return subject + "\n\n" + "\n".join(bullets)


def _merge_chunk_messages(messages: Iterable[str]) -> str:
    materialized = [_clean_message(message) for message in messages if _clean_message(message)]
    if not materialized:
        raise ContextLengthError("Diff too large even after chunking.")
    if len(materialized) == 1:
        return materialized[0]

    subject = materialized[0].splitlines()[0]
    bullets: list[str] = []
    seen: set[str] = set()
    for msg in materialized:
        for line in msg.splitlines()[1:]:
            stripped = line.strip()
            if not stripped:
                continue
            bullet = stripped if stripped.startswith(("-", "*")) else f"- {stripped}"
            if bullet not in seen:
                seen.add(bullet)
                bullets.append(bullet)

    if bullets:
        return subject + "\n\n" + "\n".join(bullets)
    return subject


def _generate_message(diff_text: str, provider_name: str):
    config = load_config()
    provider = create_provider(provider_name)

    if len(diff_text) <= MAX_DIFF_CHARS:
        return provider.generate(diff_text, config)

    chunks = chunk_diff_by_file_boundary(diff_text, MAX_DIFF_CHARS)
    partials: list[str] = []
    total = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        prefixed = f"Part {idx} of {total}:\n{chunk}"
        partials.append(provider.generate(prefixed, config))
    return _merge_chunk_messages(partials)


def _post_action(message: str) -> None:
    choice = questionary.select(
        "Action",
        choices=[
            "[C]opy",
            "[E]dit",
            "[A]ccept & commit",
            "[R]eject",
        ],
    ).ask()

    if choice == "[C]opy":
        if _copy_to_clipboard(message):
            console.print("Copied to clipboard.", style="green")
        else:
            console.print("Clipboard copy failed. Please copy manually.", style="yellow")
        return
    if choice == "[E]dit":
        edited = questionary.text("Edit commit message", default=message).ask()
        if edited:
            console.print(Panel(_clean_message(edited), title="Edited commit", border_style="cyan"))
        return
    if choice == "[A]ccept & commit":
        commit_message(message)
        console.print("Commit created.", style="green")
        return
    console.print("Rejected.", style="yellow")


@click.group(invoke_without_command=True)
@click.option("--auto", "auto_commit", is_flag=True, help="Generate and immediately commit.")
@click.version_option(version=__version__, prog_name="auto-commit")
@click.pass_context
def main(ctx: click.Context, auto_commit: bool) -> None:
    if ctx.invoked_subcommand is not None:
        return

    try:
        config = load_config()
        diff = get_staged_diff()
        with console.status(
            f"Analyzing {diff.files_changed} files (+{diff.insertions} -{diff.deletions} lines)…",
            spinner="dots",
        ):
            suggestion = _normalize_commit_message(_generate_message(diff.raw, config.provider))

        console.print(Panel(suggestion, title="Suggested commit", border_style="green"))

        if auto_commit:
            commit_message(suggestion)
            console.print("Commit created.", style="green")
            return

        _post_action(suggestion)

    except Exception as exc:  # noqa: BLE001
        log_error(exc)
        docs_url = None
        try:
            cfg = load_config()
            docs_url = PROVIDERS.get(cfg.provider, {}).get("docs_url")
        except AutoCommitError:
            docs_url = None
        console.print(render_error(exc, docs_url=docs_url))
        raise SystemExit(1) from exc


@main.command("config")
@click.option("--show", "show_only", is_flag=True, help="Show current config and exit.")
def config_cmd(show_only: bool) -> None:
    try:
        if show_only:
            cfg = load_config()
            show_config(console, cfg)
            return
        configure_interactive(console)
    except Exception as exc:  # noqa: BLE001
        log_error(exc)
        console.print(render_error(exc))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
