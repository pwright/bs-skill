#!/usr/bin/env python3
import argparse
import os
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from skill.adapters.claude import run_with_claude
from skill.adapters.codex import run_with_codex
from skill.adapters.codex_cli import run_with_codex_cli


DEFAULT_MD_TEMPLATE = """# Blockscape Map of {mdfilename}

```blockscape
{json}
```"""


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
            if name.endswith("-bs.md"):
                # Skip generated markdown outputs
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in {".md", ".markdown"}:
                yield os.path.join(dirpath, name)


def file_signature(path: str) -> Tuple[int, int]:
    stat = os.stat(path)
    return (stat.st_mtime_ns, stat.st_size)


def build_output_path(source_path: str, output_format: str) -> str:
    base, _ = os.path.splitext(source_path)
    if output_format == "md":
        return f"{base}-bs.md"
    return f"{base}.bs"


def output_exists_for(path: str, output_format: str = "bs") -> bool:
    return os.path.exists(build_output_path(path, output_format))


def generate_output(path: str, provider: str, deterministic: bool) -> str:
    prompt = f"Generate a blockscape map for the domain of\nfile: {path}"
    if provider == "claude":
        return run_with_claude(prompt, deterministic=deterministic)
    if provider == "codex-cli":
        return run_with_codex_cli(prompt, deterministic=deterministic)
    return run_with_codex(prompt, deterministic=deterministic)


def load_md_template(path: Optional[str]) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return DEFAULT_MD_TEMPLATE


def format_output(
    output: str,
    output_format: str,
    md_template: Optional[str],
    md_filename: str,
) -> str:
    cleaned = output.rstrip("\n")
    if output_format == "md":
        template = load_md_template(md_template)
        if "{json}" not in template:
            raise ValueError("Markdown template must include '{json}' placeholder")
        formatted = template.replace("{json}", cleaned).replace("{mdfilename}", md_filename)
    else:
        formatted = cleaned
    if not formatted.endswith("\n"):
        formatted += "\n"
    return formatted


def write_output(
    source_path: str,
    output: str,
    output_format: str = "bs",
    md_template: Optional[str] = None,
) -> str:
    out_path = build_output_path(source_path, output_format)
    tmp_path = f"{out_path}.tmp"
    md_filename = os.path.basename(source_path)
    formatted = format_output(output, output_format, md_template, md_filename)
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write(formatted)
    os.replace(tmp_path, out_path)
    return out_path


def scan_files(
    root: str,
    min_bytes: int,
    output_format: str = "bs",
) -> Dict[str, Tuple[int, int]]:
    seen: Dict[str, Tuple[int, int]] = {}
    for path in iter_md_files(root):
        try:
            if output_exists_for(path, output_format=output_format):
                continue
            sig = file_signature(path)
            if sig[1] < min_bytes:
                continue
            seen[path] = sig
        except FileNotFoundError:
            continue
    return seen


def confirm_initial_processing(file_count: int, min_bytes: int) -> bool:
    suffix = "" if file_count == 1 else "s"
    prompt = (
        f"--initial will process {file_count} markdown file{suffix} "
        f"(>= {min_bytes} bytes). Continue? [y/N]: "
    )
    try:
        response = input(prompt).strip().lower()
    except EOFError:
        return False
    except KeyboardInterrupt:
        print(file=sys.stderr)
        return False
    return response in {"y", "yes"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Root directory to watch")
    parser.add_argument("--provider", choices=["claude", "codex", "codex-cli"], default="codex-cli")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    parser.add_argument("--min-bytes", type=int, default=5000, help="Ignore markdown files smaller than this many bytes")
    parser.add_argument("--initial", action="store_true", help="Process existing files on startup")
    parser.add_argument("--verbose", action="store_true", help="Log processed files to stderr")
    parser.add_argument("--deterministic", action="store_true", help="Use deterministic output without calling an LLM")
    parser.add_argument("--output-format", choices=["bs", "md"], default="bs", help="File format to write alongside source markdown")
    parser.add_argument(
        "--md-template",
        help="Path to a markdown template containing a '{json}' placeholder (used when --output-format=md); '{mdfilename}' is also available",
    )
    args = parser.parse_args()
    if args.min_bytes < 0:
        parser.error("--min-bytes must be >= 0")

    root = os.path.abspath(args.root)
    seen = scan_files(root, args.min_bytes, output_format=args.output_format)

    if args.initial:
        initial_paths = sorted(seen.keys())
        if confirm_initial_processing(len(initial_paths), args.min_bytes):
            for path in initial_paths:
                try:
                    output = generate_output(path, args.provider, args.deterministic)
                    out_path = write_output(
                        path,
                        output,
                        output_format=args.output_format,
                        md_template=args.md_template,
                    )
                    if args.verbose:
                        print(f"Wrote {out_path}", file=sys.stderr)
                except Exception as exc:
                    print(f"ERROR: failed to process {path}: {exc}", file=sys.stderr)
        else:
            print("Cancelled", file=sys.stderr)
            return 1

    while True:
        time.sleep(args.interval)
        current = scan_files(root, args.min_bytes, output_format=args.output_format)

        for path, sig in current.items():
            if path not in seen or seen[path] != sig:
                try:
                    output = generate_output(path, args.provider, args.deterministic)
                    out_path = write_output(
                        path,
                        output,
                        output_format=args.output_format,
                        md_template=args.md_template,
                    )
                    if args.verbose:
                        print(f"Wrote {out_path}", file=sys.stderr)
                except Exception as exc:
                    print(f"ERROR: failed to process {path}: {exc}", file=sys.stderr)

        seen = current


if __name__ == "__main__":
    raise SystemExit(main())
