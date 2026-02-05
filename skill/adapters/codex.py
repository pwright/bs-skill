import os
from skill.core.types import Message, SkillRequest
from skill.core.skill import run_skill

BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

def run_with_codex(user_text: str) -> str:
    print(f"DEBUG: using Codex adapter base_url={BASE_URL}", flush=True)
    req = SkillRequest(messages=[Message(role="user", content=user_text)])
    res = run_skill(req)
    return res.output
