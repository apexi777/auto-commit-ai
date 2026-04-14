# FAQ

## Does auto-commit send my code to the AI provider?

Yes. Only the Git diff (changed lines) is sent, not the full codebase. Your API key is stored locally in `~/.auto_commit/config.json`.

## Can I use this without an internet connection?

No. All providers require an internet connection.

## How do I switch providers after initial setup?

Run `auto-commit config` and select a new provider.

## Is my API key stored securely?

It is stored in plain text in `~/.auto_commit/config.json` on your local machine. Never share that file. Use environment variables for CI/CD.

## The commit message is in the wrong language.

The tool auto-detects language from your diff context. You can force English by adding `"language": "en"` to your config file.

## How do I add auto-commit to my existing git hooks?

Add this to `.git/hooks/prepare-commit-msg`:

```sh
#!/bin/sh
auto-commit --auto
```

Then run:

```bash
chmod +x .git/hooks/prepare-commit-msg
```
