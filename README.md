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

#### Use Ollama at `http://localhost:11434/`

Make sure Ollama is running locally, then pull the model you want to use:

```bash
ollama pull llama3.1
```

Point the `codex` provider at Ollama's OpenAI-compatible endpoint:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_MODEL=llama3.2
```

`OPENAI_BASE_URL` should include `/v1` because this adapter sends requests to `<base>/chat/completions`.

Run with the local endpoint:

```bash
OPENAI_BASE_URL=http://localhost:11434/v1 \
OPENAI_API_KEY=ollama \
OPENAI_MODEL=llama3.2 \
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
python scripts/watch_md.py --root /path/to/docs --provider codex-cli --interval 1 --min-bytes 1000 --verbose
```

Optional flags:
- `--initial` to generate `.bs` files for existing markdown on startup (shows file count and asks for confirmation)
- `--provider` to choose `codex`, `codex-cli`, or `claude`
  Default is `codex-cli` (uses your local Codex CLI login/session)
- `--interval` to adjust polling frequency (seconds)
- `--min-bytes` to skip markdown files smaller than this size (defaults to `5000`)
- `--deterministic` to avoid LLM calls

Watcher behavior:
- Files are skipped when a sibling `.bs` file already exists. Delete or rename the `.bs` file to regenerate.

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
