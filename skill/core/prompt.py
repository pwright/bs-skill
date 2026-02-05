import os
from pathlib import Path

from .types import SkillPlan

_DEFAULT_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompt.md"


def _load_template() -> str:
    override = os.environ.get("BLOCKSCAPE_PROMPT_PATH")
    path = Path(override) if override else _DEFAULT_PROMPT_PATH
    if path.exists():
        return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Prompt template not found: {path}")


def build_prompt(plan: SkillPlan, source_text: str) -> str:
    instruction = _load_template()
    if plan.file_path:
        referenced = plan.file_path
    else:
        referenced = "the referenced content"

    instruction = instruction.replace("[referenced file]", referenced)
    user_request = plan.user_text.strip()
    if user_request:
        if plan.file_path or len(user_request) < 800:
            instruction += "\n\nUser request:\n" + user_request
    return instruction + "\n\nReferenced file content:\n" + source_text
