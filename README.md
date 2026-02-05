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

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama

cat tests/golden/simple.in | python -m skill.cli --provider codex
```

### Run with Claude

```bash
cat tests/golden/simple.in | python -m skill.cli --provider claude
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
