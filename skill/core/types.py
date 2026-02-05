from dataclasses import dataclass
from typing import Any, List, Dict

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
class SkillResult:
    output: str
