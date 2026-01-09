"""
Rendering helpers for consistent output formatting.
"""

from typing import List
from .models import ComputeOption, OptionEvaluation
from .constants import ConfidenceLevel


def format_option_output(option: ComputeOption, evaluation: OptionEvaluation) -> str:
    """Format a single option for output."""
    lines: List[str] = []
    lines.append(f"Score: {option.score:.1f}")
    lines.append(f"Recommended for: {option.best_for}")
    lines.append("")
    lines.append("Why this scored:")
    for reason in evaluation.rationale:
        lines.append(f"  • {reason}")
    lines.append("")
    lines.append("Pros:")
    for pro in option.pros:
        lines.append(f"  + {pro}")
    lines.append("")
    lines.append("Cons:")
    for con in option.cons:
        lines.append(f"  - {con}")
    lines.append("")
    lines.append("Watch out for:")
    for watch_out in option.watch_outs:
        lines.append(f"  ⚠ {watch_out}")
    return "\n".join(lines)


def format_confidence(level: ConfidenceLevel, message: str) -> str:
    """Format confidence indicator."""
    return f"Confidence / Sensitivity: {level.upper()}\n{message}"

