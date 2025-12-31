"""Unified Test Executor - Routes to appropriate entity executor and coordinates testing."""

from typing import Dict, List, Any, Optional
import logging
import uuid
from ..attacks.attack_library import AttackLibrary
from .executors import LLMExecutor, AgentExecutor, ChatbotExecutor

logger = logging.getLogger(__name__)


class TestExecutor:
    """
    Smart router for testing any AI entity (LLM, Agent, Chatbot).
    
    Flow:
    1. Load attacks for the entity type
    2. Route to appropriate executor
    3. Execute tests and compile results
    4. Return unified response
    """

    def __init__(self):
        self.executors = {
            "llm": LLMExecutor(),
            "agent": AgentExecutor(),
            "chatbot": ChatbotExecutor(),
        }

    def execute(self, entity_type: str, entity, invariants: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute unified test suite.
        
        Args:
            entity_type: 'llm', 'agent', or 'chatbot'
            entity: The entity to test (LLMProvider, Agent, or Chatbot)
            invariants: Specific invariants to test (None = all)
        
        Returns:
            Unified test results
        
        Raises:
            ValueError: If entity type or invariants are invalid
        """
        # Validate inputs
        entity_type = entity_type.lower()
        if entity_type not in self.executors:
            raise ValueError(f"Unsupported entity type: {entity_type}. Must be 'llm', 'agent', or 'chatbot'")

        if invariants is None:
            invariants = AttackLibrary.get_invariants()
        else:
            invalid = set(invariants) - set(AttackLibrary.get_invariants())
            if invalid:
                raise ValueError(f"Invalid invariants: {invalid}")

        # Generate test ID
        test_id = str(uuid.uuid4())

        # Log test start
        logger.info(f"========== TEST START ==========")
        logger.info(f"Test ID: {test_id}")
        logger.info(f"Entity Type: {entity_type}")
        logger.info(f"Invariants: {', '.join(invariants)}")

        try:
            # Load attacks for this entity type
            logger.info("Loading attack library...")
            attacks = AttackLibrary.get_all_attacks(entity_type=entity_type, invariants=invariants)

            # Log attack counts
            attack_counts = self._count_attacks(attacks)
            logger.info(f"Loaded {attack_counts['total']} total attacks")
            logger.info(f"  - Single-turn: {attack_counts['single_turn']}")
            logger.info(f"  - Multi-turn: {attack_counts['multi_turn']}")
            if 'entity_specific' in attack_counts:
                logger.info(f"  - Entity-specific: {attack_counts['entity_specific']}")

            # Route to appropriate executor
            logger.info(f"Routing to {entity_type.upper()}Executor...")
            executor = self.executors[entity_type]

            # Execute tests
            results = executor.execute(entity, attacks, test_id)

            # Enrich results
            results["entity_type"] = entity_type
            results["invariants_tested"] = invariants
            results["attack_counts"] = attack_counts

            # Log completion
            logger.info(f"========== TEST COMPLETE ==========")
            logger.info(f"Total Violations: {results.get('total_violations', 0)}")
            logger.info(f"Gate Decision: {results.get('gate_decision', 'UNKNOWN')}")

            return results

        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}", exc_info=True)
            raise

    def _count_attacks(self, attacks: Dict) -> Dict[str, int]:
        """Count attacks by type."""
        counts = {
            "single_turn": sum(
                len(prompts) for prompts in attacks.get("single_turn", {}).values()
            ),
            "multi_turn": sum(
                len(sequences) for sequences in attacks.get("multi_turn", {}).values()
            ),
            "total": 0,
        }

        # Entity-specific counts
        if "agent_specific" in attacks:
            agent_specific_count = sum(
                len(seqs) for seqs in attacks["agent_specific"].values()
            )
            counts["entity_specific"] = agent_specific_count
        elif "chatbot_specific" in attacks:
            chatbot_specific_count = sum(
                len(seqs) for seqs in attacks["chatbot_specific"].values()
            )
            counts["entity_specific"] = chatbot_specific_count

        counts["total"] = counts["single_turn"] + counts["multi_turn"] + counts.get("entity_specific", 0)

        return counts


# Global executor instance
_test_executor = None


def get_test_executor() -> TestExecutor:
    """Get or create global test executor."""
    global _test_executor
    if _test_executor is None:
        _test_executor = TestExecutor()
    return _test_executor
