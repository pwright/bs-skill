import os
import re
from typing import Optional, Tuple

from .types import SkillPlan


def _title_from_content(lines) -> Optional[str]:
    for line in lines:
        match = re.match(r"^\s*#\s+(.+)", line)
        if match:
            return match.group(1).strip()
    for line in lines:
        cleaned = line.strip()
        if cleaned:
            return cleaned[:80]
    return None


def load_source(plan: SkillPlan) -> Tuple[str, str]:
    source_text = plan.user_text
    title_hint = "Blockscape Map"
    if plan.file_path:
        with open(plan.file_path, "r", encoding="utf-8", errors="ignore") as handle:
            source_text = handle.read()
        base = os.path.splitext(os.path.basename(plan.file_path))[0]
        title_hint = base.replace("_", " ").replace("-", " ").title()
    detected_title = _title_from_content(source_text.splitlines())
    if detected_title:
        title_hint = detected_title
    return source_text, title_hint
