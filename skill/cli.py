#!/usr/bin/env python3
import sys
import argparse
from skill.adapters.claude import run_with_claude
from skill.adapters.codex import run_with_codex
from skill.adapters.codex_cli import run_with_codex_cli

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=["claude", "codex", "codex-cli"], required=True)
    p.add_argument("--output", help="Write output to a file instead of stdout")
    p.add_argument("--deterministic", action="store_true", help="Use deterministic output without calling an LLM")
    args = p.parse_args()

    text = sys.stdin.read()
    print("DEBUG: read stdin", file=sys.stderr, flush=True)

    if args.provider == "claude":
        out = run_with_claude(text, deterministic=args.deterministic)
    elif args.provider == "codex-cli":
        out = run_with_codex_cli(text, deterministic=args.deterministic)
    else:
        out = run_with_codex(text, deterministic=args.deterministic)

    if not out.endswith("\n"):
        out += "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(out)
    else:
        sys.stdout.write(out)

if __name__ == "__main__":
    main()
