import json
import os
import urllib.request

from skill.core.executor import execute
from skill.core.planner import plan
from skill.core.prompt import build_prompt
from skill.core.source import load_source
from skill.core.types import Message, SkillRequest

def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} must be set to call the LLM")
    return value


def _call_anthropic(prompt: str) -> str:
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    api_key = _require_env("ANTHROPIC_API_KEY")
    model = _require_env("ANTHROPIC_MODEL")

    url = base_url.rstrip("/") + "/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 4000,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    try:
        return data["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected LLM response shape: {data}") from exc


def run_with_claude(user_text: str, deterministic: bool = False) -> str:
    req = SkillRequest(messages=[Message(role="user", content=user_text)])
    if deterministic:
        skill_plan = plan(req, deterministic=True)
        return execute(skill_plan)

    skill_plan = plan(req, deterministic=False)
    source_text, _title_hint = load_source(skill_plan)
    prompt = build_prompt(skill_plan, source_text)
    return _call_anthropic(prompt)
