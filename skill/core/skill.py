from .planner import plan
from .executor import execute
from .types import SkillRequest, SkillResult

def run_skill(req: SkillRequest) -> SkillResult:
    steps = plan(req)
    result = execute(steps)
    return SkillResult(output=result)
