from dataclasses import dataclass
from typing import Set, List
from preflight.core.behavior import Behavior


@dataclass
class Invariant:
    name: str
    description: str
    severity: str  # "CRITICAL", "MAJOR", "MINOR"
    violation_behaviors: Set[Behavior]
    prompts: List[str]
