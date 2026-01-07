"""
Tarka — Cloud Compute Referee
A constraint-aware decision-support tool for AWS compute choices.
"""

from .models import ComputeOption, EvaluationResult, EvaluationInputs
from .tarka_core import evaluate, get_compute_options, get_confidence
from .rendering import format_option_output, format_confidence

__all__ = [
    "ComputeOption",
    "EvaluationResult",
    "EvaluationInputs",
    "evaluate",
    "get_compute_options",
    "get_confidence",
    "format_option_output",
    "format_confidence",
]

