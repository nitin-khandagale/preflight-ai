from dataclasses import dataclass, field
from typing import Set, List, Optional
from preflight.core.behavior import Behavior


@dataclass
class Invariant:
    name: str
    description: str
    severity: str  # "CRITICAL", "MAJOR", "MINOR"
    violation_behaviors: Set[Behavior]
    prompts: List[str]
    multi_turn_sequences: List = field(default_factory=list)  # List of MultiTurnSequence objects
