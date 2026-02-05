#!/usr/bin/env python3
import argparse
import os
import sys
import time
from typing import Dict, Iterable, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from skill.adapters.claude import run_with_claude
from skill.adapters.codex import run_with_codex
from skill.adapters.codex_cli import run_with_codex_cli


def iter_md_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".") and d not in {"__pycache__", "node_modules"}
        ]
        for name in filenames:
            if name.startswith("."):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in {".md", ".markdown"}:
                yield os.path.join(dirpath, name)


def file_signature(path: str) -> Tuple[int, int]:
    stat = os.stat(path)
    return (stat.st_mtime_ns, stat.st_size)


def generate_output(path: str, provider: str, deterministic: bool) -> str:
    prompt = f"Generate a blockscape map for the domain of\nfile: {path}"
    if provider == "claude":
        return run_with_claude(prompt, deterministic=deterministic)
    if provider == "codex-cli":
        return run_with_codex_cli(prompt, deterministic=deterministic)
    return run_with_codex(prompt, deterministic=deterministic)


def write_output(source_path: str, output: str) -> str:
    base, _ = os.path.splitext(source_path)
    out_path = f"{base}.bs"
    tmp_path = f"{out_path}.tmp"
    if not output.endswith("\n"):
        output += "\n"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write(output)
    os.replace(tmp_path, out_path)
    return out_path


def scan_files(root: str) -> Dict[str, Tuple[int, int]]:
    seen: Dict[str, Tuple[int, int]] = {}
    for path in iter_md_files(root):
        try:
            seen[path] = file_signature(path)
        except FileNotFoundError:
            continue
    return seen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Root directory to watch")
    parser.add_argument("--provider", choices=["claude", "codex", "codex-cli"], default="codex")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    parser.add_argument("--initial", action="store_true", help="Process existing files on startup")
    parser.add_argument("--verbose", action="store_true", help="Log processed files to stderr")
    parser.add_argument("--deterministic", action="store_true", help="Use deterministic output without calling an LLM")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    seen = scan_files(root)

    if args.initial:
        for path in sorted(seen.keys()):
            try:
                output = generate_output(path, args.provider, args.deterministic)
                out_path = write_output(path, output)
                if args.verbose:
                    print(f"Wrote {out_path}", file=sys.stderr)
            except Exception as exc:
                print(f"ERROR: failed to process {path}: {exc}", file=sys.stderr)

    while True:
        time.sleep(args.interval)
        current = scan_files(root)

        for path, sig in current.items():
            if path not in seen or seen[path] != sig:
                try:
                    output = generate_output(path, args.provider, args.deterministic)
                    out_path = write_output(path, output)
                    if args.verbose:
                        print(f"Wrote {out_path}", file=sys.stderr)
                except Exception as exc:
                    print(f"ERROR: failed to process {path}: {exc}", file=sys.stderr)

        seen = current


if __name__ == "__main__":
    raise SystemExit(main())
