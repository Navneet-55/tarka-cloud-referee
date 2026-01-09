"""
Core evaluation logic for Tarka Cloud Compute Referee.
Deterministic, rule-based scoring with no external dependencies.
"""

from typing import Dict, List, Tuple
from .models import (
    ComputeOption, EvaluationInputs, EvaluationResult,
    OptionEvaluation, ScoreContribution
)
from .constants import (
    SCORE_TRAFFIC_MATCH,
    SCORE_CONTROL_MATCH,
    SCORE_COST_MATCH,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD,
    OPTION_LAMBDA,
    OPTION_ECS,
    OPTION_EC2
)


def get_compute_options() -> List[ComputeOption]:
    """Get all available compute options with their characteristics."""
    return [
        ComputeOption(
            name=OPTION_LAMBDA,
            pros=[
                "No server management",
                "Automatic scaling",
                "Pay per execution"
            ],
            cons=[
                "Cold start latency",
                "Execution time limits",
                "Limited runtime control"
            ],
            best_for="Event-driven or bursty workloads"
        ),
        ComputeOption(
            name=OPTION_ECS,
            pros=[
                "Good balance of control and abstraction",
                "Works well with containers",
                "Predictable runtime"
            ],
            cons=[
                "More setup than Lambda",
                "Container image management required"
            ],
            best_for="Microservices with steady traffic"
        ),
        ComputeOption(
            name=OPTION_EC2,
            pros=[
                "Maximum infrastructure control",
                "Custom networking and storage",
                "Suitable for legacy workloads"
            ],
            cons=[
                "Highest operational overhead",
                "Manual scaling unless automated",
                "Requires patching and monitoring"
            ],
            best_for="Workloads requiring full control"
        ),
    ]


def _calculate_score_contributions(
    option: ComputeOption,
    inputs: EvaluationInputs
) -> List[ScoreContribution]:
    """Calculate score contributions for an option based on inputs."""
    contributions = []
    weights = inputs.weights
    
    if option.name == "AWS Lambda":
        if inputs.traffic == "bursty":
            points = 2.0 * weights.get("traffic", 1.0)
            contributions.append(ScoreContribution(
                factor="traffic",
                points=points,
                reason="Bursty traffic pattern (+2)"
            ))
        if inputs.cost == "sensitive":
            points = 1.0 * weights.get("cost", 1.0)
            contributions.append(ScoreContribution(
                factor="cost",
                points=points,
                reason="Cost-sensitive workload (+1)"
            ))
    
    elif option.name == "AWS ECS (Fargate)":
        if inputs.traffic == "steady":
            points = 2.0 * weights.get("traffic", 1.0)
            contributions.append(ScoreContribution(
                factor="traffic",
                points=points,
                reason="Steady traffic pattern (+2)"
            ))
        if inputs.control == "medium":
            points = 1.0 * weights.get("control", 1.0)
            contributions.append(ScoreContribution(
                factor="control",
                points=points,
                reason="Medium control requirement (+1)"
            ))
    
    elif option.name == "AWS EC2":
        if inputs.control == "high":
            points = 2.0 * weights.get("control", 1.0)
            contributions.append(ScoreContribution(
                factor="control",
                points=points,
                reason="High control requirement (+2)"
            ))
    
    return contributions


def _generate_rationale(
    option: ComputeOption,
    inputs: EvaluationInputs
) -> List[str]:
    """Generate deterministic rationale for why an option scored as it did."""
    reasons = []
    contributions = _calculate_score_contributions(option, inputs)
    
    # Add positive contributions
    for contrib in contributions:
        if contrib.points > 0:
            reasons.append(contrib.reason)
    
    # Add contextual notes
    if option.name == "AWS Lambda":
        if inputs.control == "high":
            reasons.append("High control needs may limit fit")
        if inputs.traffic == "steady":
            reasons.append("Steady traffic may not need Lambda's auto-scaling")
    
    elif option.name == "AWS ECS (Fargate)":
        if inputs.traffic == "bursty":
            reasons.append("Bursty traffic may prefer serverless")
        if inputs.control == "high":
            reasons.append("High control needs may require EC2")
    
    elif option.name == "AWS EC2":
        if inputs.traffic == "bursty":
            reasons.append("Bursty traffic may prefer serverless")
        if inputs.cost == "sensitive":
            reasons.append("Cost-sensitive workloads may prefer pay-per-use")
        if inputs.control == "low":
            reasons.append("Low control needs may prefer managed services")
    
    return reasons if reasons else ["Base score (no specific matches)"]


def _score_options(
    options: List[ComputeOption],
    inputs: EvaluationInputs
) -> List[ComputeOption]:
    """Score all options based on inputs. Modifies options in place."""
    # Reset scores
    for opt in options:
        opt.score = 0.0
    
    # Calculate contributions and accumulate scores
    for opt in options:
        contributions = _calculate_score_contributions(opt, inputs)
        for contrib in contributions:
            opt.score += contrib.points
    
    # Normalize weights if needed
    weights = inputs.weights
    if weights:
        total = sum(weights.values())
        if total > 0:
            # Normalize to maintain relative importance
            for opt in options:
                opt.score = opt.score * (len(weights) / total)
    
    # Rank by score (descending)
    return sorted(options, key=lambda x: x.score, reverse=True)


def _get_what_would_change(
    top_option: ComputeOption,
    inputs: EvaluationInputs
) -> List[str]:
    """Generate rule-based suggestions for what would change the decision."""
    suggestions = []
    
    if top_option.name == "AWS Lambda":
        if inputs.traffic == "bursty":
            suggestions.append("If workload becomes steady/always-on, ECS/Fargate or EC2 may become better fit")
        if inputs.control == "low":
            suggestions.append("If control needs increase, consider ECS/Fargate or EC2")
        if inputs.cost == "sensitive":
            suggestions.append("If cost becomes less critical, ECS/Fargate may offer better runtime control")
        suggestions.append("If execution time exceeds Lambda limits, move to ECS/Fargate or EC2")
        suggestions.append("If you need custom networking or storage, EC2 may be required")
    
    elif top_option.name == "AWS ECS (Fargate)":
        if inputs.traffic == "steady":
            suggestions.append("If traffic becomes highly bursty, Lambda may be more cost-effective")
        if inputs.control == "medium":
            suggestions.append("If control needs decrease, Lambda may simplify operations")
            suggestions.append("If control needs increase significantly, EC2 may be required")
        suggestions.append("If container management overhead becomes too high, consider Lambda or EC2")
    
    elif top_option.name == "AWS EC2":
        if inputs.control == "high":
            suggestions.append("If ops appetite decreases, ECS/Fargate or Lambda may reduce overhead")
        if inputs.traffic == "steady":
            suggestions.append("If traffic becomes bursty, Lambda may be more cost-effective")
        suggestions.append("If you don't need full infrastructure control, ECS/Fargate or Lambda may be simpler")
        suggestions.append("If cost becomes critical, Lambda's pay-per-use model may be better")
    
    return suggestions if suggestions else ["Consider reviewing all trade-offs as requirements evolve"]


def get_confidence(ranked: List[ComputeOption]) -> Tuple[str, str]:
    """Calculate confidence based on score gap between rank 1 and 2."""
    if len(ranked) < 2:
        return "High", "Score gap calculation requires at least 2 options"
    
    gap = ranked[0].score - ranked[1].score
    if gap >= 3:
        return "High", f"Score gap of {gap:.1f} indicates clear preference"
    elif gap >= 2:
        return "Medium", f"Score gap of {gap:.1f} suggests moderate confidence"
    else:
        return "Low", f"Score gap of {gap:.1f} indicates close competition"


def evaluate(inputs: EvaluationInputs) -> EvaluationResult:
    """
    Main evaluation function. Returns complete evaluation result.
    
    Args:
        inputs: EvaluationInputs object with traffic, control, cost, and optional weights
        
    Returns:
        EvaluationResult with ranked options, details, confidence, and recommendations
    """
    # Get all options
    options = get_compute_options()
    
    # Score and rank options
    ranked = _score_options(options, inputs)
    
    # Build option details
    option_details = {}
    for idx, opt in enumerate(ranked, 1):
        contributions = _calculate_score_contributions(opt, inputs)
        rationale = _generate_rationale(opt, inputs)
        
        option_details[opt.name] = OptionEvaluation(
            option=opt,
            rank=idx,
            contributions=contributions,
            rationale=rationale
        )
    
    # Calculate confidence
    conf_level, conf_msg = get_confidence(ranked)
    
    # Generate "what would change" suggestions
    what_would_change = _get_what_would_change(ranked[0], inputs) if ranked else []
    
    return EvaluationResult(
        ranked_options=ranked,
        option_details=option_details,
        confidence_level=conf_level,
        confidence_message=conf_msg,
        inputs=inputs,
        what_would_change=what_would_change
    )
