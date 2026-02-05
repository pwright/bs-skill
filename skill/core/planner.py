import os
import re
from typing import Optional

from .types import SkillPlan, SkillRequest

_PATH_HINT_RE = re.compile(r"\b(?:file|path)\s*:\s*(.+)", re.IGNORECASE)

def _clean_token(token: str) -> str:
    return token.strip().strip("\"'()[]<>.,;:")

def _find_existing_path(text: str) -> Optional[str]:
    candidate = text.strip()
    if "\n" not in candidate and " " not in candidate:
        candidate = _clean_token(candidate)
        if candidate and os.path.isfile(candidate):
            return candidate

    for line in text.splitlines():
        match = _PATH_HINT_RE.search(line)
        if match:
            candidate = _clean_token(match.group(1))
            if candidate and os.path.isfile(candidate):
                return candidate

    for match in re.finditer(r"\(([^)]+)\)", text):
        candidate = _clean_token(match.group(1))
        if candidate and os.path.isfile(candidate):
            return candidate

    for token in re.split(r"\s+", text):
        token = token.lstrip("@")
        candidate = _clean_token(token)
        if candidate and os.path.isfile(candidate):
            return candidate

    return None

def plan(req: SkillRequest, deterministic: bool = False) -> SkillPlan:
    user_text = req.messages[-1].content.strip()
    file_path = _find_existing_path(user_text)
    want_series = bool(re.search(r"\bseries\b", user_text, re.IGNORECASE))
    want_wardley = bool(re.search(r"\bwardley\b", user_text, re.IGNORECASE))
    return SkillPlan(
        user_text=user_text,
        file_path=file_path,
        want_series=want_series,
        want_wardley=want_wardley,
        deterministic=deterministic,
    )
