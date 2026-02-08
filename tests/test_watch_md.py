import importlib.util
from pathlib import Path


WATCH_MD_PATH = Path(__file__).resolve().parents[1] / "scripts" / "watch_md.py"
WATCH_MD_SPEC = importlib.util.spec_from_file_location("watch_md", WATCH_MD_PATH)
assert WATCH_MD_SPEC and WATCH_MD_SPEC.loader
WATCH_MD_MODULE = importlib.util.module_from_spec(WATCH_MD_SPEC)
WATCH_MD_SPEC.loader.exec_module(WATCH_MD_MODULE)
scan_files = WATCH_MD_MODULE.scan_files


def test_scan_files_skips_when_bs_output_exists(tmp_path):
    skipped = tmp_path / "skip.md"
    skipped.write_text("0123456789", encoding="utf-8")
    (tmp_path / "skip.bs").write_text("{}", encoding="utf-8")

    kept = tmp_path / "keep.md"
    kept.write_text("0123456789", encoding="utf-8")

    seen = scan_files(str(tmp_path), min_bytes=1)

    assert str(skipped) not in seen
    assert str(kept) in seen
