import importlib.util
import os
import time
from pathlib import Path


WATCH_MD_PATH = Path(__file__).resolve().parents[1] / "scripts" / "watch_md.py"
WATCH_MD_SPEC = importlib.util.spec_from_file_location("watch_md", WATCH_MD_PATH)
assert WATCH_MD_SPEC and WATCH_MD_SPEC.loader
WATCH_MD_MODULE = importlib.util.module_from_spec(WATCH_MD_SPEC)
WATCH_MD_SPEC.loader.exec_module(WATCH_MD_MODULE)
scan_files = WATCH_MD_MODULE.scan_files
build_output_path = WATCH_MD_MODULE.build_output_path
format_output = WATCH_MD_MODULE.format_output
DEFAULT_MD_TEMPLATE = WATCH_MD_MODULE.DEFAULT_MD_TEMPLATE


def test_scan_files_skips_when_bs_output_exists(tmp_path):
    skipped = tmp_path / "skip.md"
    skipped.write_text("0123456789", encoding="utf-8")
    (tmp_path / "skip.bs").write_text("{}", encoding="utf-8")

    kept = tmp_path / "keep.md"
    kept.write_text("0123456789", encoding="utf-8")

    seen = scan_files(str(tmp_path), min_bytes=1)

    assert str(skipped) not in seen
    assert str(kept) in seen


def test_scan_files_skips_when_md_output_exists(tmp_path):
    source = tmp_path / "example.md"
    source.write_text("0123456789", encoding="utf-8")
    (tmp_path / "example-bs.md").write_text("# existing", encoding="utf-8")

    seen = scan_files(str(tmp_path), min_bytes=1, output_format="md")

    assert str(source) not in seen


def test_iter_md_files_skips_generated_dash_bs(tmp_path):
    real = tmp_path / "real.md"
    real.write_text("content", encoding="utf-8")
    generated = tmp_path / "note-bs.md"
    generated.write_text("generated", encoding="utf-8")

    seen = scan_files(str(tmp_path), min_bytes=1, output_format="md")

    assert str(real) in seen
    assert str(generated) not in seen


def test_build_output_path_uses_dash_bs_md_suffix():
    path = build_output_path("/docs/topic.md", output_format="md")
    assert path == "/docs/topic-bs.md"


def test_format_output_wraps_json_in_default_template():
    json_text = '{ "hello": "world" }'
    formatted = format_output(
        json_text,
        output_format="md",
        md_template=None,
        md_filename="topic.md",
    )
    expected = (
        DEFAULT_MD_TEMPLATE.replace("{json}", json_text).replace("{mdfilename}", "topic.md") + "\n"
    )
    assert formatted == expected


def test_format_output_accepts_custom_template(tmp_path):
    template_path = tmp_path / "tmpl.md"
    template_path.write_text("X\n{json}\nY", encoding="utf-8")
    json_text = "{}"

    formatted = format_output(
        json_text,
        output_format="md",
        md_template=str(template_path),
        md_filename="topic.md",
    )

    assert formatted == "X\n{}\nY\n"


def test_format_output_requires_placeholder(tmp_path):
    template_path = tmp_path / "bad.md"
    template_path.write_text("no placeholder here", encoding="utf-8")

    try:
        format_output("{}", output_format="md", md_template=str(template_path), md_filename="x.md")
    except ValueError as exc:
        assert "placeholder" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing placeholder")


def test_scan_files_skips_older_than_max_age(tmp_path):
    recent = tmp_path / "recent.md"
    recent.write_text("0123456789", encoding="utf-8")

    old = tmp_path / "old.md"
    old.write_text("content", encoding="utf-8")
    ten_days_ago = time.time() - 10 * 24 * 60 * 60
    os.utime(old, (ten_days_ago, ten_days_ago))

    seen = scan_files(str(tmp_path), min_bytes=1, max_age_days=5)

    assert str(recent) in seen
    assert str(old) not in seen
