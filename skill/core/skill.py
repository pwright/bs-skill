from .planner import plan
from .executor import execute
from .types import SkillRequest, SkillResult

def run_skill(req: SkillRequest) -> SkillResult:
    print("DEBUG: running skill core", flush=True)
    steps = plan(req)
    print(f"DEBUG: plan={steps}", flush=True)
    result = execute(steps)
    return SkillResult(output=result)
