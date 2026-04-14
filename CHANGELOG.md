# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to Semantic Versioning.

## [Unreleased]

## [0.1.0] - 2026-04-14

### Added
- Production-ready `auto-commit` CLI with Rich UX and interactive confirmation flow.
- Provider registry for OpenAI, Anthropic, Gemini, DeepSeek, Grok, and Mistral.
- Shared `OpenAICompatibleProvider` base for OpenAI-compatible APIs.
- Git staged diff analysis with binary/lock filtering and file-boundary chunking.
- Config system with interactive TUI, local JSON persistence, and env var fallback.
- Structured error handling with Rich panels and persistent error logging.
- Test suite for git extraction, configuration behavior, and provider integration contracts.
- Project docs expansion: FAQ, provider comparison, contributing guide, and GitHub templates.

### Changed
- Migrated Gemini provider from deprecated `google-generativeai` to `google-genai` SDK.
- Added CLI version flag support (`auto-commit --version`).
- Updated provider tests to cover Gemini message generation via `google.genai`.

### Security
- Hardened dependency minimum versions for mid-2025 stable baselines.
- Added strict pytest warnings policy to fail fast on unexpected warnings.
- Added `.gitignore` and `.env.example` to prevent accidental credential leakage.
