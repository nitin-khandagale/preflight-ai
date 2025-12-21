from enum import Enum

class Behavior(Enum):
    REFUSE = "refuse"
    DEFLECT = "deflect"
    PARTIAL_COMPLIANCE = "partial_compliance"
    FULL_COMPLIANCE = "full_compliance"


class DisclosureDepth(Enum):
    NONE = 0          # Boundary assertion only
    ABSTRACT = 1      # High-level description
    INSTANTIATED = 2  # Structured / operational disclosure
