import os
import shlex
import subprocess
import tempfile
from pathlib import Path

from skill.core.executor import execute
from skill.core.planner import plan
from skill.core.prompt import build_prompt
from skill.core.source import load_source
from skill.core.types import Message, SkillRequest


def _truthy(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def _build_command() -> list:
    cmd = ["codex", "exec", "--color", "never"]

    cd_root = os.environ.get("CODEX_CLI_CD")
    if cd_root:
        cmd += ["--cd", cd_root]

    model = os.environ.get("CODEX_CLI_MODEL")
    if model:
        cmd += ["--model", model]

    if _truthy(os.environ.get("CODEX_CLI_SKIP_GIT_CHECK", "")):
        cmd.append("--skip-git-repo-check")

    extra = os.environ.get("CODEX_CLI_ARGS")
    if extra:
        cmd += shlex.split(extra)

    return cmd


def _call_codex_cli(prompt: str) -> str:
    cmd = _build_command()
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        run = subprocess.run(
            cmd + ["--output-last-message", tmp_path, "-"],
            input=prompt,
            text=True,
            capture_output=True,
        )
        if run.returncode != 0:
            detail = (run.stderr or run.stdout or "").strip()
            raise RuntimeError(f"codex exec failed: {detail}")

        output = Path(tmp_path).read_text(encoding="utf-8")
        if not output.strip():
            raise RuntimeError("codex produced empty output")
        return output
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def run_with_codex_cli(user_text: str, deterministic: bool = False) -> str:
    req = SkillRequest(messages=[Message(role="user", content=user_text)])
    if deterministic:
        skill_plan = plan(req, deterministic=True)
        return execute(skill_plan)

    skill_plan = plan(req, deterministic=False)
    source_text, _title_hint = load_source(skill_plan)
    prompt = build_prompt(skill_plan, source_text)
    return _call_codex_cli(prompt)
