from __future__ import annotations

import fnmatch
import re
import subprocess
from dataclasses import dataclass

from auto_commit.errors import GitNotFoundError, NoDiffError

MAX_DIFF_CHARS = 120_000


@dataclass
class GitDiff:
    raw: str
    files_changed: int
    insertions: int
    deletions: int


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise GitNotFoundError("git not found") from exc


def _should_skip_file(path: str) -> bool:
    if path.startswith("node_modules/"):
        return True
    if fnmatch.fnmatch(path, "*.lock"):
        return True
    return False


def _split_sections(diff: str) -> list[str]:
    if not diff.strip():
        return []
    sections = re.split(r"(?=^diff --git a/)", diff, flags=re.MULTILINE)
    return [section for section in sections if section.strip()]


def _section_path(section: str) -> str:
    first = section.splitlines()[0]
    match = re.match(r"diff --git a/(.+?) b/", first)
    return match.group(1) if match else ""


def _filter_diff(diff: str) -> str:
    filtered: list[str] = []
    for section in _split_sections(diff):
        path = _section_path(section)
        if _should_skip_file(path):
            continue
        if "Binary files " in section or "GIT binary patch" in section:
            continue
        filtered.append(section)
    return "\n".join(filtered).strip() + ("\n" if filtered else "")


def chunk_diff_by_file_boundary(diff: str, max_chars: int = MAX_DIFF_CHARS) -> list[str]:
    if len(diff) <= max_chars:
        return [diff]

    chunks: list[str] = []
    current = ""
    for section in _split_sections(diff):
        if len(section) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(section), max_chars):
                chunks.append(section[i : i + max_chars])
            continue

        if current and len(current) + len(section) > max_chars:
            chunks.append(current)
            current = section
        else:
            current += section

    if current:
        chunks.append(current)

    return chunks


def _stats() -> tuple[int, int, int]:
    result = _run_git(["diff", "--cached", "--numstat"])
    if result.returncode != 0:
        return 0, 0, 0

    files = 0
    ins = 0
    dele = 0
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        files += 1
        add_s, del_s, _ = parts
        if add_s.isdigit():
            ins += int(add_s)
        if del_s.isdigit():
            dele += int(del_s)
    return files, ins, dele


def get_staged_diff() -> GitDiff:
    result = _run_git(["diff", "--cached"])
    if result.returncode != 0:
        raise GitNotFoundError(result.stderr.strip() or "git diff failed")

    cleaned = _filter_diff(result.stdout)
    if not cleaned.strip():
        raise NoDiffError("No staged changes")

    files, ins, dele = _stats()
    return GitDiff(raw=cleaned, files_changed=files, insertions=ins, deletions=dele)


def commit_message(message: str) -> None:
    result = _run_git(["commit", "-m", message])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git commit failed")
