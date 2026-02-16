#!/usr/bin/env python3
"""Convert .bs files to Markdown using the Blockscape template.

This script scans a directory tree for `.bs` files, and for each one writes a
Markdown companion named `<basename>-bs.md` using the standard Blockscape
template (or a custom template if provided). Existing outputs are skipped unless
`--overwrite` is set.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse formatting helpers and default template from the watcher script
from scripts import watch_md  # type: ignore


def iter_bs_files(root: str) -> Iterable[str]:
    """Yield paths to .bs files under ``root``, skipping common noise dirs."""

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".") and d not in {"__pycache__", "node_modules"}
        ]
        for name in filenames:
            if name.startswith("."):
                continue
            if name.lower().endswith(".bs"):
                yield os.path.join(dirpath, name)


def convert_file(
    path: str,
    md_template: Optional[str] = None,
    overwrite: bool = False,
) -> Optional[str]:
    """Convert a single .bs file to ``-bs.md``.

    Returns the output path when written, or ``None`` if skipped.
    """

    out_path = watch_md.build_output_path(path, output_format="md")

    if not overwrite and os.path.exists(out_path):
        return None

    json_text = Path(path).read_text(encoding="utf-8")
    md_filename = f"{Path(path).stem}.md"

    formatted = watch_md.format_output(
        json_text,
        output_format="md",
        md_template=md_template,
        md_filename=md_filename,
    )

    tmp_path = f"{out_path}.tmp"
    Path(tmp_path).write_text(formatted, encoding="utf-8")
    os.replace(tmp_path, out_path)
    return out_path


def convert_tree(
    root: str,
    md_template: Optional[str] = None,
    overwrite: bool = False,
    verbose: bool = False,
) -> List[str]:
    """Process all .bs files under ``root``. Returns list of written paths."""

    written: List[str] = []
    for path in iter_bs_files(root):
        try:
            out = convert_file(path, md_template=md_template, overwrite=overwrite)
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"ERROR: failed to convert {path}: {exc}", file=sys.stderr)
            continue

        if out:
            written.append(out)
            if verbose:
                print(f"Wrote {out}", file=sys.stderr)
    return written


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Directory to scan recursively (defaults to current directory)",
    )
    parser.add_argument(
        "--md-template",
        dest="md_template",
        help="Path to a markdown template containing '{json}' and optionally '{mdfilename}'",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rewrite outputs even when the target -bs.md file already exists",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log written files to stderr",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    written = convert_tree(
        root,
        md_template=args.md_template,
        overwrite=args.overwrite,
        verbose=args.verbose,
    )

    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
