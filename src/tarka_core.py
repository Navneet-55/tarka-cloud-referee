"""
Core evaluation logic for Tarka Cloud Compute Referee.
Deterministic, rule-based scoring with no external dependencies.
"""

from typing import Dict, Tuple, Optional
from .models import (
    ComputeOption, EvaluationInputs, EvaluationResult,
    OptionEvaluation, ScoreContribution, ScoredOption
)
from .constants import (
    SCORE_TRAFFIC_MATCH,
    SCORE_CONTROL_HIGH_MATCH,
    SCORE_CONTROL_MEDIUM_MATCH,
    SCORE_COST_MATCH,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD,
    OPTION_LAMBDA,
    OPTION_ECS,
    OPTION_EC2,
    ConfidenceLevel,
    SCORING_RULES,
    ScoringRule
)


def get_compute_options() -> tuple[ComputeOption, ...]:
    """Get all available compute options with their characteristics.
    
    Returns:
        tuple[ComputeOption, ...]: A tuple containing three compute options:
            AWS Lambda, AWS ECS (Fargate), and AWS EC2, each with their
            pros, cons, and best use cases.
    
    Example:
        >>> options = get_compute_options()
        >>> len(options)
        3
        >>> options[0].name
        'AWS Lambda'
    """
    return (
        ComputeOption(
            name=OPTION_LAMBDA,
            pros=(
                "No server management",
                "Automatic scaling",
                "Pay per execution"
            ),
            cons=(
                "Cold start latency",
                "Execution time limits",
                "Limited runtime control"
            ),
            best_for="Event-driven or bursty workloads"
        ),
        ComputeOption(
            name=OPTION_ECS,
            pros=(
                "Good balance of control and abstraction",
                "Works well with containers",
                "Predictable runtime"
            ),
            cons=(
                "More setup than Lambda",
                "Container image management required"
            ),
            best_for="Microservices with steady traffic"
        ),
        ComputeOption(
            name=OPTION_EC2,
            pros=(
                "Maximum infrastructure control",
                "Custom networking and storage",
                "Suitable for legacy workloads"
            ),
            cons=(
                "Highest operational overhead",
                "Manual scaling unless automated",
                "Requires patching and monitoring"
            ),
            best_for="Workloads requiring full control"
        ),
    )


def _get_matching_rules(
    option: ComputeOption,
    inputs: EvaluationInputs
) -> tuple[ScoringRule, ...]:
    """Get all scoring rules that match the given option and inputs.
    
    Args:
        option: The compute option to find matching rules for.
        inputs: The evaluation inputs containing traffic, control, and cost preferences.
    
    Returns:
        tuple[ScoringRule, ...]: A tuple of scoring rules that apply to this option
            given the current inputs. Empty tuple if no rules match.
    
    Note:
        Rules are matched based on option name and condition values. Each rule
        specifies a condition type (traffic/control/cost) and value that must
        match the inputs.
    """
    matching_rules: list[ScoringRule] = []
    
    for rule in SCORING_RULES:
        # Check if rule applies to this option
        if rule.option_name != option.name:
            continue
        
        # Check if the condition matches the inputs
        if rule.condition_type == "traffic" and inputs.traffic == rule.condition_value:
            matching_rules.append(rule)
        elif rule.condition_type == "control" and inputs.control == rule.condition_value:
            matching_rules.append(rule)
        elif rule.condition_type == "cost" and inputs.cost == rule.condition_value:
            matching_rules.append(rule)
    
    return tuple(matching_rules)


def _calculate_score_contributions(
    option: ComputeOption,
    inputs: EvaluationInputs
) -> tuple[ScoreContribution, ...]:
    """Calculate score contributions for an option based on inputs.
    
    Uses the SCORING_RULES configuration to determine which rules apply
    to the given option and inputs, then applies weights to calculate
    the final contribution points.
    
    Args:
        option: The compute option to score.
        inputs: The evaluation inputs with traffic, control, cost, and weights.
    
    Returns:
        tuple[ScoreContribution, ...]: A tuple of score contributions, each
            containing the factor, points, and reason for the contribution.
    
    Example:
        >>> inputs = EvaluationInputs(traffic="bursty", control="low", cost="sensitive")
        >>> lambda_option = get_compute_options()[0]
        >>> contributions = _calculate_score_contributions(lambda_option, inputs)
        >>> len(contributions)
        2
        >>> contributions[0].factor
        'traffic'
    """
    contributions: list[ScoreContribution] = []
    weights: Dict[str, float] = inputs.weights
    
    # Get matching rules from configuration
    matching_rules: tuple[ScoringRule, ...] = _get_matching_rules(option, inputs)
    
    # Convert rules to contributions with weights applied
    for rule in matching_rules:
        points: float = rule.points * weights.get(rule.condition_type, 1.0)
        contributions.append(ScoreContribution(
            factor=rule.condition_type,
            points=points,
            reason=rule.reason
        ))
    
    return tuple(contributions)


def _get_positive_rationale(
    contributions: tuple[ScoreContribution, ...]
) -> tuple[str, ...]:
    """Extract positive contribution reasons.
    
    Args:
        contributions: Score contributions to extract reasons from.
    
    Returns:
        tuple[str, ...]: Reasons for all positive contributions.
    """
    reasons: list[str] = []
    for contrib in contributions:
        if contrib.points > 0:
            reasons.append(contrib.reason)
    return tuple(reasons)


def _get_contextual_notes(
    option: ComputeOption,
    inputs: EvaluationInputs
) -> tuple[str, ...]:
    """Generate contextual notes about why an option may not be ideal.
    
    Provides warnings or caveats about the option based on the inputs,
    helping users understand potential limitations or mismatches.
    
    Args:
        option: The compute option to generate notes for.
        inputs: The evaluation inputs to check against.
    
    Returns:
        tuple[str, ...]: Contextual notes about potential concerns or limitations.
    """
    notes: list[str] = []
    
    if option.name == OPTION_LAMBDA:
        if inputs.control == "high":
            notes.append("High control needs may limit fit")
        if inputs.traffic == "steady":
            notes.append("Steady traffic may not need Lambda's auto-scaling")
    
    elif option.name == OPTION_ECS:
        if inputs.traffic == "bursty":
            notes.append("Bursty traffic may prefer serverless")
        if inputs.control == "high":
            notes.append("High control needs may require EC2")
    
    elif option.name == OPTION_EC2:
        if inputs.traffic == "bursty":
            notes.append("Bursty traffic may prefer serverless")
        if inputs.cost == "sensitive":
            notes.append("Cost-sensitive workloads may prefer pay-per-use")
        if inputs.control == "low":
            notes.append("Low control needs may prefer managed services")
    
    return tuple(notes)


def _generate_rationale(
    option: ComputeOption,
    inputs: EvaluationInputs
) -> tuple[str, ...]:
    """Generate deterministic rationale for why an option scored as it did.
    
    Combines positive scoring reasons with contextual notes to provide
    a complete explanation of the option's score and fit.
    
    Args:
        option: The compute option to generate rationale for.
        inputs: The evaluation inputs used for scoring.
    
    Returns:
        tuple[str, ...]: A tuple of rationale strings explaining the score.
            Always returns at least one string (default message if no matches).
    """
    contributions: tuple[ScoreContribution, ...] = _calculate_score_contributions(option, inputs)
    
    # Get positive contributions
    positive_reasons: tuple[str, ...] = _get_positive_rationale(contributions)
    
    # Get contextual notes
    contextual_notes: tuple[str, ...] = _get_contextual_notes(option, inputs)
    
    # Combine all reasons
    all_reasons: tuple[str, ...] = positive_reasons + contextual_notes
    
    return all_reasons if all_reasons else ("Base score (no specific matches)",)


def _score_options(
    options: tuple[ComputeOption, ...],
    inputs: EvaluationInputs
) -> tuple[ScoredOption, ...]:
    """Score all options based on inputs. Returns tuple of ScoredOption objects.
    
    Calculates scores for each option by summing weighted contributions,
    applies weight normalization if needed, and returns options sorted
    by score in descending order.
    
    Args:
        options: The compute options to score.
        inputs: The evaluation inputs with traffic, control, cost, and weights.
    
    Returns:
        tuple[ScoredOption, ...]: Options with their scores, sorted by score
            (highest first). Each ScoredOption contains the original option
            and its calculated score.
    
    Note:
        This function is pure - it creates new ScoredOption objects rather
        than modifying the input options.
    """
    scored_options: list[ScoredOption] = []
    
    # Calculate contributions and accumulate scores
    for opt in options:
        contributions: tuple[ScoreContribution, ...] = _calculate_score_contributions(opt, inputs)
        score: float = sum(contrib.points for contrib in contributions)
        scored_options.append(ScoredOption(option=opt, score=score))
    
    # Normalize weights if needed
    weights: Dict[str, float] = inputs.weights
    total: float = sum(weights.values())
    if total > 0 and total != len(weights):
        # Normalize to maintain relative importance
        normalization_factor: float = len(weights) / total
        scored_options = [
            ScoredOption(option=so.option, score=so.score * normalization_factor)
            for so in scored_options
        ]
    
    # Rank by score (descending)
    return tuple(sorted(scored_options, key=lambda x: x.score, reverse=True))


def _get_lambda_change_suggestions(inputs: EvaluationInputs) -> tuple[str, ...]:
    """Get suggestions for what would change Lambda recommendation.
    
    Args:
        inputs: Current evaluation inputs.
    
    Returns:
        tuple[str, ...]: Suggestions for scenarios where Lambda may no longer be optimal.
    """
    suggestions: list[str] = []
    
    if inputs.traffic == "bursty":
        suggestions.append("If workload becomes steady/always-on, ECS/Fargate or EC2 may become better fit")
    if inputs.control == "low":
        suggestions.append("If control needs increase, consider ECS/Fargate or EC2")
    if inputs.cost == "sensitive":
        suggestions.append("If cost becomes less critical, ECS/Fargate may offer better runtime control")
    suggestions.append("If execution time exceeds Lambda limits, move to ECS/Fargate or EC2")
    suggestions.append("If you need custom networking or storage, EC2 may be required")
    
    return tuple(suggestions)


def _get_ecs_change_suggestions(inputs: EvaluationInputs) -> tuple[str, ...]:
    """Get suggestions for what would change ECS recommendation.
    
    Args:
        inputs: Current evaluation inputs.
    
    Returns:
        tuple[str, ...]: Suggestions for scenarios where ECS may no longer be optimal.
    """
    suggestions: list[str] = []
    
    if inputs.traffic == "steady":
        suggestions.append("If traffic becomes highly bursty, Lambda may be more cost-effective")
    if inputs.control == "medium":
        suggestions.append("If control needs decrease, Lambda may simplify operations")
        suggestions.append("If control needs increase significantly, EC2 may be required")
    suggestions.append("If container management overhead becomes too high, consider Lambda or EC2")
    
    return tuple(suggestions)


def _get_ec2_change_suggestions(inputs: EvaluationInputs) -> tuple[str, ...]:
    """Get suggestions for what would change EC2 recommendation.
    
    Args:
        inputs: Current evaluation inputs.
    
    Returns:
        tuple[str, ...]: Suggestions for scenarios where EC2 may no longer be optimal.
    """
    suggestions: list[str] = []
    
    if inputs.control == "high":
        suggestions.append("If ops appetite decreases, ECS/Fargate or Lambda may reduce overhead")
    if inputs.traffic == "steady":
        suggestions.append("If traffic becomes bursty, Lambda may be more cost-effective")
    suggestions.append("If you don't need full infrastructure control, ECS/Fargate or Lambda may be simpler")
    suggestions.append("If cost becomes critical, Lambda's pay-per-use model may be better")
    
    return tuple(suggestions)


def _get_what_would_change(
    top_option: ComputeOption,
    inputs: EvaluationInputs
) -> tuple[str, ...]:
    """Generate rule-based suggestions for what would change the decision.
    
    Provides actionable insights about what changes in requirements or
    constraints would lead to a different recommendation.
    
    Args:
        top_option: The currently recommended option.
        inputs: The evaluation inputs that led to this recommendation.
    
    Returns:
        tuple[str, ...]: Suggestions for what would change the recommendation.
    """
    if top_option.name == OPTION_LAMBDA:
        return _get_lambda_change_suggestions(inputs)
    elif top_option.name == OPTION_ECS:
        return _get_ecs_change_suggestions(inputs)
    elif top_option.name == OPTION_EC2:
        return _get_ec2_change_suggestions(inputs)
    else:
        return ("Consider reviewing all trade-offs as requirements evolve",)


def get_confidence(ranked: tuple[ScoredOption, ...]) -> Tuple[ConfidenceLevel, str]:
    """Calculate confidence based on score gap between rank 1 and 2.
    
    Confidence indicates how clear the preference is for the top option.
    A larger score gap means higher confidence in the recommendation.
    
    Args:
        ranked: Scored options sorted by score (highest first).
    
    Returns:
        Tuple[ConfidenceLevel, str]: A tuple containing:
            - Confidence level: "High", "Medium", or "Low"
            - Confidence message: Explanation of the confidence level
    
    Note:
        - High confidence: gap >= 3.0 points
        - Medium confidence: gap >= 2.0 points
        - Low confidence: gap < 2.0 points
    """
    if len(ranked) < 2:
        return "High", "Score gap calculation requires at least 2 options"
    
    gap: float = ranked[0].score - ranked[1].score
    if gap >= CONFIDENCE_HIGH_THRESHOLD:
        return "High", f"Score gap of {gap:.1f} indicates clear preference"
    elif gap >= CONFIDENCE_MEDIUM_THRESHOLD:
        return "Medium", f"Score gap of {gap:.1f} suggests moderate confidence"
    else:
        return "Low", f"Score gap of {gap:.1f} indicates close competition"


def evaluate(inputs: EvaluationInputs) -> EvaluationResult:
    """Main evaluation function. Returns complete evaluation result.
    
    This is the primary entry point for evaluating compute options. It scores
    all available options based on the provided inputs, ranks them, calculates
    confidence, and generates explanations and recommendations.
    
    Args:
        inputs: EvaluationInputs object containing:
            - traffic: Traffic pattern ("bursty" or "steady")
            - control: Infrastructure control level ("low", "medium", or "high")
            - cost: Cost sensitivity ("sensitive" or "flexible")
            - weights: Optional dict of weights for each factor (default: all 1.0)
    
    Returns:
        EvaluationResult containing:
            - ranked_options: Tuple of ScoredOption objects sorted by score
            - option_details: Dict mapping option names to OptionEvaluation
            - confidence_level: "High", "Medium", or "Low"
            - confidence_message: Explanation of confidence
            - inputs: The original inputs used
            - what_would_change: Suggestions for what would change the decision
    
    Raises:
        InvalidInputError: If inputs are invalid (via EvaluationInputs validation)
    
    Example:
        >>> inputs = EvaluationInputs(
        ...     traffic="bursty",
        ...     control="low",
        ...     cost="sensitive"
        ... )
        >>> result = evaluate(inputs)
        >>> result.top_option.name
        'AWS Lambda'
        >>> result.confidence_level
        'High'
        >>> len(result.ranked_options)
        3
    
    Note:
        This function is deterministic - the same inputs always produce
        the same results. No external APIs or random elements are used.
    """
    # Get all options
    options: tuple[ComputeOption, ...] = get_compute_options()
    
    # Score and rank options
    ranked: tuple[ScoredOption, ...] = _score_options(options, inputs)
    
    # Build option details
    option_details: Dict[str, OptionEvaluation] = {}
    for idx, scored_opt in enumerate(ranked, 1):
        opt: ComputeOption = scored_opt.option
        contributions: tuple[ScoreContribution, ...] = _calculate_score_contributions(opt, inputs)
        rationale: tuple[str, ...] = _generate_rationale(opt, inputs)
        
        option_details[opt.name] = OptionEvaluation(
            option=opt,
            rank=idx,
            contributions=contributions,
            rationale=rationale
        )
    
    # Calculate confidence
    conf_level: ConfidenceLevel
    conf_msg: str
    conf_level, conf_msg = get_confidence(ranked)
    
    # Generate "what would change" suggestions
    what_would_change: tuple[str, ...] = _get_what_would_change(ranked[0].option, inputs) if ranked else ()
    
    return EvaluationResult(
        ranked_options=ranked,
        option_details=option_details,
        confidence_level=conf_level,
        confidence_message=conf_msg,
        inputs=inputs,
        what_would_change=what_would_change
    )
