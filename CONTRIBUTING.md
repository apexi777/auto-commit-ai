# Contributing

## Development setup

```bash
git clone https://github.com/apexi777/auto-commit-ai
cd auto-commit-ai
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

## Adding a new AI provider

1. Add provider metadata to `auto_commit/auto_commit/ai/__init__.py` inside `PROVIDERS`.
2. If the API is OpenAI-compatible, subclass `OpenAICompatibleProvider` in `auto_commit/auto_commit/ai/` and set `base_url`.
3. If not OpenAI-compatible, implement `AIProvider.generate(diff, config)` directly.
4. Wire the class mapping in the provider factory.
5. Add or update mocked tests in `tests/test_providers.py`.
6. Verify CLI flow with `auto-commit config` and `auto-commit --auto`.

## Commit message rules

- Use Conventional Commits (`feat`, `fix`, `docs`, `refactor`, etc.).
- Prefer concise subject lines (<=72 chars).
- Use `auto-commit` itself to generate commit messages for changes.

## Pull request checklist

- [ ] Tests added or updated for behavior changes.
- [ ] `pytest -q` passes locally.
- [ ] README/docs updated when user-facing behavior changes.
- [ ] CHANGELOG entry added under `[Unreleased]`.
- [ ] PR description includes problem, solution, and verification steps.
