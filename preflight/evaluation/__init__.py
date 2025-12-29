"""
Evaluation package initialization
"""

from preflight.evaluation.logger import EvaluationLogger
from preflight.evaluation.hook import enable_evaluation_logging, disable_evaluation_logging, log_if_enabled

__all__ = ['EvaluationLogger', 'enable_evaluation_logging', 'disable_evaluation_logging', 'log_if_enabled']
