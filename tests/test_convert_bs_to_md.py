import importlib.util
from pathlib import Path


CONVERT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "convert_bs_to_md.py"
SPEC = importlib.util.spec_from_file_location("convert_bs_to_md", CONVERT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

convert_file = MODULE.convert_file
convert_tree = MODULE.convert_tree
DEFAULT_MD_TEMPLATE = MODULE.watch_md.DEFAULT_MD_TEMPLATE


def test_convert_file_writes_markdown_with_default_template(tmp_path):
    src = tmp_path / "topic.bs"
    json_text = '{ "hello": "world" }'
    src.write_text(json_text, encoding="utf-8")

    out_path = convert_file(str(src))

    assert out_path is not None
    content = Path(out_path).read_text(encoding="utf-8")
    expected = (
        DEFAULT_MD_TEMPLATE.replace("{json}", json_text).replace("{mdfilename}", "topic.md") + "\n"
    )
    assert content == expected


def test_convert_tree_skips_existing_outputs_without_overwrite(tmp_path):
    src = tmp_path / "keep.bs"
    src.write_text("{}", encoding="utf-8")
    out = tmp_path / "keep-bs.md"
    out.write_text("# existing", encoding="utf-8")

    written = convert_tree(str(tmp_path))

    assert written == []
    assert out.read_text(encoding="utf-8") == "# existing"


def test_convert_file_overwrites_when_flag_set(tmp_path):
    src = tmp_path / "redo.bs"
    src.write_text("{}", encoding="utf-8")
    out = tmp_path / "redo-bs.md"
    out.write_text("# old", encoding="utf-8")

    convert_file(str(src), overwrite=True)

    assert out.read_text(encoding="utf-8").startswith("# Blockscape Map of redo.md")
