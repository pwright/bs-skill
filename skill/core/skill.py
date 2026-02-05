from .planner import plan
from .executor import execute
from .types import SkillRequest, SkillResult

def run_skill(req: SkillRequest, deterministic: bool = False) -> SkillResult:
    steps = plan(req, deterministic=deterministic)
    result = execute(steps)
    return SkillResult(output=result)
