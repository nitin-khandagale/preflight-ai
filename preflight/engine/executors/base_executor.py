"""Base executor for all entity types."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging


logger = logging.getLogger(__name__)


class BaseExecutor(ABC):
    """Abstract base executor for all entity types."""

    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.logger = logger

    @abstractmethod
    def execute(self, entity, attacks: Dict, test_id: str) -> Dict[str, Any]:
        """
        Execute tests on the entity.
        
        Args:
            entity: The entity to test (LLM provider, Agent, or Chatbot)
            attacks: Dictionary with 'single_turn', 'multi_turn', and optional entity-specific attacks
            test_id: Unique test identifier
        
        Returns:
            Test results dictionary
        """
        pass

    def log_step(self, step: str, status: str = ""):
        """Log a test step."""
        msg = f"[{self.entity_type.upper()}] {step}"
        if status:
            msg += f" {status}"
        self.logger.info(msg)

    def classify_behavior(self, response: str, context: List[Dict] = None) -> str:
        """
        Classify model behavior from response.
        
        Returns: REFUSE, DEFLECT, PARTIAL_COMPLIANCE, or FULL_COMPLIANCE
        """
        from ..engine.classifier import ResponseBehaviorClassifier
        
        classifier = ResponseBehaviorClassifier()
        return classifier.classify(response)
