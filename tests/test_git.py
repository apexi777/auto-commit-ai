from __future__ import annotations

import subprocess

import pytest

from auto_commit.git import chunk_diff_by_file_boundary, get_staged_diff
from auto_commit.errors import NoDiffError


class DummyCompletedProcess(subprocess.CompletedProcess[str]):
    def __init__(self, args, returncode=0, stdout="", stderr=""):
        super().__init__(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


def test_empty_diff_raises_NoDiffError(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args, **kwargs):
        return DummyCompletedProcess(args=args[0], stdout="")

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(NoDiffError):
        get_staged_diff()


def test_large_diff_is_chunked() -> None:
    section = "diff --git a/a.py b/a.py\n" + ("+x\n" * 70_000)
    section2 = "diff --git a/b.py b/b.py\n" + ("+y\n" * 70_000)
    diff = section + section2

    chunks = chunk_diff_by_file_boundary(diff, max_chars=120_000)

    assert len(chunks) >= 2
    assert all(chunk for chunk in chunks)


def test_binary_files_stripped(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd, **kwargs):
        if cmd[-1] == "--numstat":
            return DummyCompletedProcess(cmd, stdout="1\t0\timage.png\n")
        return DummyCompletedProcess(
            cmd,
            stdout=(
                "diff --git a/image.png b/image.png\n"
                "Binary files a/image.png and b/image.png differ\n"
                "diff --git a/code.py b/code.py\n"
                "+print('ok')\n"
            ),
        )

    monkeypatch.setattr("subprocess.run", fake_run)
    diff = get_staged_diff()

    assert "Binary files" not in diff.raw
    assert "code.py" in diff.raw


def test_lock_files_stripped(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd, **kwargs):
        if cmd[-1] == "--numstat":
            return DummyCompletedProcess(cmd, stdout="1\t0\tpoetry.lock\n1\t0\tsrc/app.py\n")
        return DummyCompletedProcess(
            cmd,
            stdout=(
                "diff --git a/poetry.lock b/poetry.lock\n"
                "+new lock\n"
                "diff --git a/src/app.py b/src/app.py\n"
                "+print('app')\n"
            ),
        )

    monkeypatch.setattr("subprocess.run", fake_run)
    diff = get_staged_diff()

    assert "poetry.lock" not in diff.raw
    assert "src/app.py" in diff.raw
