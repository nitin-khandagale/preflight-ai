"""
Optional evaluation hook for the runner.
Enable this to auto-log classifications without affecting workflow.
Simply import and call enable_evaluation_logging() at startup.
"""

from preflight.evaluation import EvaluationLogger

_logger = None
_enabled = False


def enable_evaluation_logging():
    """Enable automatic logging of all classifications."""
    global _logger, _enabled
    _logger = EvaluationLogger()
    _enabled = True
    print("[INFO] Evaluation logging enabled")


def disable_evaluation_logging():
    """Disable automatic logging."""
    global _enabled
    _enabled = False


def log_if_enabled(response_text, behavior, invariant_name=None, prompt_text=None):
    """
    Log a classification if logging is enabled.
    Called optionally from the runner.
    
    Args:
        response_text: The model response
        behavior: The Behavior classification
        invariant_name: Which invariant
        prompt_text: The original prompt
    """
    if _enabled and _logger:
        _logger.log_classification(
            response_text=response_text,
            classified_as=behavior,
            invariant_name=invariant_name,
            prompt_text=prompt_text
        )
