import json
import os
import urllib.error
import urllib.request

from skill.core.executor import execute
from skill.core.planner import plan
from skill.core.prompt import build_prompt
from skill.core.source import load_source
from skill.core.types import Message, SkillRequest


def _call_openai_chat(prompt: str) -> str:
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")

    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    if model:
        payload["model"] = model
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    try:
        with urllib.request.urlopen(req, timeout=1020) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "replace").strip()
        except Exception:
            detail = ""
        if exc.code == 401:
            raise RuntimeError(
                "HTTP 401 Unauthorized for provider 'codex'. "
                "This provider uses OPENAI_API_KEY auth. "
                "If you are logged into Codex CLI, run with --provider codex-cli instead."
            ) from exc
        raise RuntimeError(
            f"HTTP error from provider 'codex' ({exc.code}): {detail or exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error from provider 'codex': {exc}") from exc
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected LLM response shape: {data}") from exc


def run_with_codex(user_text: str, deterministic: bool = False) -> str:
    req = SkillRequest(messages=[Message(role="user", content=user_text)])
    if deterministic:
        skill_plan = plan(req, deterministic=True)
        return execute(skill_plan)

    skill_plan = plan(req, deterministic=False)
    source_text, _title_hint = load_source(skill_plan)
    prompt = build_prompt(skill_plan, source_text)
    return _call_openai_chat(prompt)
