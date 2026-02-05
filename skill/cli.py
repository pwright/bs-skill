#!/usr/bin/env python3
import sys
import argparse
from skill.adapters.claude import run_with_claude
from skill.adapters.codex import run_with_codex

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=["claude", "codex"], required=True)
    p.add_argument("--output", help="Write output to a file instead of stdout")
    args = p.parse_args()

    text = sys.stdin.read()
    print("DEBUG: read stdin", file=sys.stderr, flush=True)

    if args.provider == "claude":
        out = run_with_claude(text)
    else:
        out = run_with_codex(text)

    if not out.endswith("\n"):
        out += "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(out)
    else:
        sys.stdout.write(out)

if __name__ == "__main__":
    main()
