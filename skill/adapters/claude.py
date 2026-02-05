from skill.core.types import Message, SkillRequest
from skill.core.skill import run_skill

def run_with_claude(user_text: str) -> str:
    print("DEBUG: using Claude adapter", flush=True)
    req = SkillRequest(messages=[Message(role="user", content=user_text)])
    res = run_skill(req)
    return res.output
