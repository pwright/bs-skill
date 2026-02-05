# Multi-Provider Skill Skeleton

This is a minimal, production-shaped skeleton for building a single "skill" that can run against:

- Claude (Anthropic)
- Codex / OpenAI-compatible APIs
- Ollama (via OpenAI-compatible local endpoint)

## Features

- Provider-neutral core
- Thin adapters per model backend
- stdin -> stdout CLI
- stderr for debug
- Golden-test friendly
- Parallel-safe

## Quick start

### Run with Codex / Ollama

LLM mode (default):

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_MODEL=llama3.1

cat tests/golden/simple.in | python -m skill.cli --provider codex
```

Codex CLI mode (uses local `codex exec` instead of HTTP):

```bash
cat tests/golden/simple.in | python -m skill.cli --provider codex-cli
```

Optional Codex CLI env overrides:
- `CODEX_CLI_MODEL` to select a model
- `CODEX_CLI_CD` to set `--cd`
- `CODEX_CLI_SKIP_GIT_CHECK=1` to set `--skip-git-repo-check`
- `CODEX_CLI_ARGS` for extra `codex exec` args

Deterministic mode (no LLM call):

```bash
cat tests/golden/simple.in | python -m skill.cli --provider codex --deterministic
```

### Run with Claude

LLM mode (default):

```bash
export ANTHROPIC_API_KEY=your_key
export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

cat tests/golden/simple.in | python -m skill.cli --provider claude
```

Deterministic mode (no LLM call):

```bash
cat tests/golden/simple.in | python -m skill.cli --provider claude --deterministic
```

### Watch a directory of markdown files

Generate `.bs` files alongside any `.md`/`.markdown` file that changes:

```bash
python scripts/watch_md.py --root /path/to/docs --provider codex --interval 1 --verbose
```

Optional flags:
- `--initial` to generate `.bs` files for existing markdown on startup
- `--provider` to choose `codex`, `codex-cli`, or `claude`
- `--interval` to adjust polling frequency (seconds)
- `--deterministic` to avoid LLM calls

### Prompt template

LLM mode loads instructions from `prompt.md` at the repo root. Override with:

```bash
export BLOCKSCAPE_PROMPT_PATH=/path/to/prompt.md
```

### Tests

```bash
just test
```

## Layout

- skill/core      : model-agnostic logic
- skill/adapters  : provider glue
- skill/cli.py    : stdin/stdout entrypoint
- tests/golden    : golden fixtures

Adapters are disposable. Core is the product.
