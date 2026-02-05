#!/usr/bin/env python3
import sys
import argparse
from skill.adapters.claude import run_with_claude
from skill.adapters.codex import run_with_codex

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=["claude", "codex"], required=True)
    args = p.parse_args()

    text = sys.stdin.read()
    print("DEBUG: read stdin", file=sys.stderr, flush=True)

    if args.provider == "claude":
        out = run_with_claude(text)
    else:
        out = run_with_codex(text)

    sys.stdout.write(out)

if __name__ == "__main__":
    main()
