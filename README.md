# _         _             ____                            _ _
#| |  _   _| |_ ___      / ___|___  _ __ ___  _ __ ___  (_) |_
#| | | | | | __/ _ \____| |   / _ \| '_ ` _ \| '_ ` _ \ | | __|
#| | | |_| | || (_) |____| |__| (_) | | | | | | | | | | || | |_
#|_|  \__,_|\__\___/      \____\___/|_| |_| |_|_| |_| |_|/ |\__|
#                                                           |__/

AI-powered git commit messages from the command line.

![PyPI](https://img.shields.io/pypi/v/auto-commit-ai)
![Python](https://img.shields.io/pypi/pyversions/auto-commit-ai)
![License](https://img.shields.io/github/license/apexi777/auto-commit-ai)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

## Demo

```bash
$ git add auto_commit/auto_commit/gemini_provider.py
$ auto-commit

Analyzing 1 files (+24 -10 lines)…

╭─ Suggested commit ─────────────────────────────────────────────╮
│ refactor(gemini): migrate SDK integration to google-genai      │
│                                                                │
│ - replace deprecated google-generativeai client usage          │
│ - configure GenerateContentConfig for tokens and temperature   │
│ - keep provider interface compatible with existing flow        │
╰────────────────────────────────────────────────────────────────╯

[C]opy  [E]dit  [A]ccept & commit  [R]eject
```

auto-commit in action

## Features

- 6 AI providers with curated model lists (OpenAI 3, Anthropic 3, Gemini 2, DeepSeek 2, Grok 3, Mistral 3).
- Smart diff chunking for large repositories using file boundaries.
- Interactive configuration TUI powered by Rich and questionary.
- Conventional Commits output format with concise subject/body structure.
- One-command install from PyPI.

## Quick Install

```bash
pip install auto-commit-ai
```

Then configure:

```bash
auto-commit config
```

Then use:

```bash
git add .
auto-commit
```

## 📦 Installation

### Requirements

Before you start, make sure you have:

| Requirement | Minimum version | Check with              |
|-------------|----------------|-------------------------|
| Python      | 3.10+          | `python --version`      |
| Git         | any            | `git --version`         |
| pip         | 23+            | `pip --version`         |

---

### Option A — Install from PyPI (recommended)

The easiest way. Works on macOS, Linux, and Windows.

```bash
pip install auto-commit-ai
```

Verify the installation:

```bash
auto-commit --version
```

---

### Option B — Install from source (for contributors)

```bash
# 1. Clone the repository
git clone https://github.com/apexi777/auto-commit-ai.git
cd auto-commit-ai

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv

# macOS / Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Verify
auto-commit --version
```

---

## 🔑 Setup: getting your API key

You only need **one** API key — for whichever provider
you choose. Pick any from the table below:

| Provider  | Free tier | Get your key                                      |
|-----------|-----------|---------------------------------------------------|
| OpenAI    | No        | https://platform.openai.com/api-keys             |
| Anthropic | No        | https://console.anthropic.com/keys               |
| Gemini    | Yes ✓     | https://aistudio.google.com/apikey               |
| DeepSeek  | Yes ✓     | https://platform.deepseek.com/api_keys           |
| Grok      | No        | https://console.x.ai                             |
| Mistral   | Yes ✓     | https://console.mistral.ai/api-keys              |

> 💡 **Not sure which to pick?** Start with **Gemini** or
> **DeepSeek** — both offer a free tier with no credit card
> required.

---

## ⚙️ First-time configuration

Run the interactive setup wizard:

```bash
auto-commit config
```

You will be guided through three steps:

```text
? Select AI provider:
  ❯ Anthropic
    OpenAI
    Gemini
    DeepSeek
    Grok
    Mistral

? Select model:
  ❯ claude-sonnet-4-5
    claude-opus-4-5
    claude-haiku-4-5

? Enter your API key: sk-ant-****
```

Your settings are saved to `~/.auto_commit/config.json`.

**Alternatively**, set an environment variable to skip
the config step entirely:

```bash
# macOS / Linux — add to ~/.bashrc or ~/.zshrc
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

---

## 🚀 Usage

### Basic workflow

```bash
# 1. Make changes to your code
# 2. Stage them as usual
git add .

# 3. Run auto-commit — it analyzes the diff and suggests a message
auto-commit
```

Example output:

```text
╭─ Suggested commit ──────────────────────────────────╮
│  feat(auth): add JWT refresh token support           │
│                                                      │
│  - implement token rotation on each request          │
│  - add 401 handler with automatic retry              │
│  - store refresh token in httpOnly cookie            │
╰──────────────────────────────────────────────────────╯

  [C] Copy   [E] Edit   [A] Accept & commit   [R] Reject
```

### One-shot mode (no prompts)

```bash
auto-commit --auto
# Generates the message and runs git commit immediately
```

### View or change settings

```bash
auto-commit config          # open interactive menu
auto-commit config --show   # print current config
```

---

## 🛠 Troubleshooting

| Problem                            | Solution                                        |
|------------------------------------|-------------------------------------------------|
| `command not found: auto-commit`   | Make sure pip's bin dir is in your PATH.        |
|                                    | Try: `python -m auto_commit`                    |
| `Invalid API key`                  | Re-run `auto-commit config` and re-enter key    |
| `No staged changes`                | Run `git add .` first                           |
| `Account out of credits`           | Top up balance or switch provider               |
| Slow response on large repos       | Normal — large diffs are chunked automatically  |

Full error logs are written to `~/.auto_commit/error.log`.

## Providers Table

| Provider  | Models                          | Env Variable      |
|-----------|---------------------------------|-------------------|
| OpenAI    | gpt-4o, gpt-4-turbo, gpt-3.5-turbo | OPENAI_API_KEY |
| Anthropic | claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5 | ANTHROPIC_API_KEY |
| Gemini    | gemini-2.0-flash, gemini-1.5-pro | GEMINI_API_KEY |
| DeepSeek  | deepseek-chat, deepseek-reasoner | DEEPSEEK_API_KEY |
| Grok      | grok-3, grok-3-mini, grok-2 | XAI_API_KEY |
| Mistral   | mistral-large-latest, mistral-small-latest, codestral-latest | MISTRAL_API_KEY |

## Commands Reference

| Command | Description |
|---------|-------------|
| `auto-commit` | Generate commit message |
| `auto-commit --auto` | Generate + commit instantly |
| `auto-commit config` | Open interactive settings |
| `auto-commit config --show` | Print current configuration |

## Configuration

Config file path: `~/.auto_commit/config.json`

Environment variables take priority over values stored in the config file.

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-5",
  "api_keys": {
    "openai": "",
    "anthropic": "",
    "gemini": "",
    "deepseek": "",
    "grok": "",
    "mistral": ""
  },
  "language": "auto",
  "max_tokens": 512,
  "temperature": 0.3
}
```

## Contributing

```bash
git clone https://github.com/apexi777/auto-commit-ai
cd auto-commit-ai
pip install -e ".[dev]"
pytest -q
```

Guidelines:
- Use Conventional Commits.
- Add or update tests for any new provider behavior.
- Include a clear PR description: problem, solution, and verification steps.

## License

MIT License — Copyright (c) 2026 Babich Andrey
