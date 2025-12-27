from preflight.attacks.instruction_authority import instruction_authority
from preflight.attacks.information_boundary import information_boundary
from preflight.attacks.instruction_hierarchy import instruction_hierarchy
from preflight.attacks.role_integrity import role_integrity
from preflight.attacks.capability_claims import capability_claims
from preflight.attacks.hardful_action_refusal import harmful_action_refusal

ALL_INVARIANTS = [
    instruction_authority,
    information_boundary,
    instruction_hierarchy,
    role_integrity,
    capability_claims,
    harmful_action_refusal,
]
