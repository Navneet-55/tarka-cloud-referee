"""
Rendering helpers for consistent output formatting.
"""

from .models import ComputeOption, OptionEvaluation, ScoredOption
from .constants import ConfidenceLevel


def format_option_output(scored_option: ScoredOption, evaluation: OptionEvaluation) -> str:
    """Format a single option for output.
    
    Creates a formatted string representation of an option including its score,
    best use case, rationale, pros, cons, and watch-outs.
    
    Args:
        scored_option: The ScoredOption containing the option and its score.
        evaluation: The OptionEvaluation with detailed evaluation information.
    
    Returns:
        str: A formatted multi-line string suitable for console output.
    """
    option: ComputeOption = scored_option.option
    lines: list[str] = []
    lines.append(f"Score: {scored_option.score:.1f}")
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
    """Format confidence indicator.
    
    Args:
        level: The confidence level ("High", "Medium", or "Low").
        message: The confidence message explaining the level.
    
    Returns:
        str: A formatted string showing confidence level and message.
    """
    return f"Confidence / Sensitivity: {level.upper()}\n{message}"

