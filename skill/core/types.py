from dataclasses import dataclass
from typing import Any, List, Dict, Optional

@dataclass
class Message:
    role: str
    content: str

@dataclass
class ToolCall:
    name: str
    args: Dict[str, Any]

@dataclass
class SkillRequest:
    messages: List[Message]

@dataclass
class SkillPlan:
    user_text: str
    file_path: Optional[str]
    want_series: bool
    want_wardley: bool

@dataclass
class SkillResult:
    output: str
