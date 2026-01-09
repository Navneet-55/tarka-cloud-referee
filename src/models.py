"""
Data models for Tarka Cloud Compute Referee.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .constants import (
    TrafficPattern,
    ControlLevel,
    CostSensitivity,
    ConfidenceLevel,
    DEFAULT_WEIGHTS,
    VALID_TRAFFIC_PATTERNS,
    VALID_CONTROL_LEVELS,
    VALID_COST_SENSITIVITIES
)
from .exceptions import InvalidInputError


@dataclass(frozen=True)
class ComputeOption:
    """Represents a compute option with its characteristics.
    
    Attributes:
        name: The name of the compute option (e.g., "AWS Lambda").
        pros: Tuple of advantages or benefits of this option.
        cons: Tuple of disadvantages or limitations of this option.
        best_for: Description of the ideal use case for this option.
    
    Properties:
        watch_outs: Returns the cons (same as cons attribute, for semantic clarity).
    
    Note:
        This dataclass is immutable (frozen=True) to prevent accidental modifications.
    """
    name: str
    pros: tuple[str, ...]
    cons: tuple[str, ...]
    best_for: str
    
    @property
    def watch_outs(self) -> tuple[str, ...]:
        """Watch-outs are derived from cons.
        
        Returns:
            tuple[str, ...]: The same tuple as cons, providing semantic clarity
                for UI/display purposes.
        """
        return self.cons


@dataclass(frozen=True)
class EvaluationInputs:
    """Inputs for evaluation.
    
    Attributes:
        traffic: Traffic pattern - "bursty" for unpredictable spikes,
            "steady" for consistent load.
        control: Infrastructure control level - "low" for managed services,
            "medium" for balanced control, "high" for full control.
        cost: Cost sensitivity - "sensitive" for cost-conscious workloads,
            "flexible" for less cost-constrained scenarios.
        weights: Optional dict of weights for each factor. Defaults to all 1.0.
            Keys should be "traffic", "control", "cost". Pass None to use defaults.
    
    Raises:
        InvalidInputError: If any input value is invalid or weights are negative/empty.
    
    Note:
        This dataclass is immutable (frozen=True). Validation occurs in __post_init__.
    """
    traffic: TrafficPattern
    control: ControlLevel
    cost: CostSensitivity
    weights: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        """Validate inputs and set default weights if needed."""
        # Validate traffic
        if self.traffic not in VALID_TRAFFIC_PATTERNS:
            raise InvalidInputError(f"traffic must be one of {VALID_TRAFFIC_PATTERNS}, got '{self.traffic}'")
        
        # Validate control
        if self.control not in VALID_CONTROL_LEVELS:
            raise InvalidInputError(f"control must be one of {VALID_CONTROL_LEVELS}, got '{self.control}'")
        
        # Validate cost
        if self.cost not in VALID_COST_SENSITIVITIES:
            raise InvalidInputError(f"cost must be one of {VALID_COST_SENSITIVITIES}, got '{self.cost}'")
        
        # Set default weights if None provided
        if self.weights is None:
            object.__setattr__(self, 'weights', DEFAULT_WEIGHTS.copy())
        
        # Validate weights (after potentially setting defaults)
        if not self.weights:
            raise InvalidInputError("weights dictionary cannot be empty")
        
        for key, value in self.weights.items():
            if value < 0:
                raise InvalidInputError(f"weight for '{key}' must be non-negative, got {value}")


@dataclass(frozen=True)
class ScoreContribution:
    """Contribution of a factor to an option's score.
    
    Attributes:
        factor: The factor that contributed (e.g., "traffic", "control", "cost").
        points: The number of points contributed to the total score.
        reason: Human-readable explanation of why this contribution was made.
    """
    factor: str
    points: float
    reason: str


@dataclass(frozen=True)
class ScoredOption:
    """A compute option with its calculated score.
    
    Attributes:
        option: The ComputeOption being scored.
        score: The calculated score for this option based on inputs.
    
    Note:
        This separates the immutable option definition from the calculated
        score, allowing options to be scored multiple times with different inputs.
    """
    option: ComputeOption
    score: float


@dataclass(frozen=True)
class OptionEvaluation:
    """Evaluation details for a single option.
    
    Attributes:
        option: The ComputeOption being evaluated.
        rank: The rank of this option (1 = best, 2 = second best, etc.).
        contributions: Tuple of ScoreContribution objects explaining the score.
        rationale: Tuple of human-readable reasons explaining why this option
            scored as it did, including both positive and cautionary notes.
    """
    option: ComputeOption
    rank: int
    contributions: tuple[ScoreContribution, ...]
    rationale: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationResult:
    """Complete evaluation result.
    
    Attributes:
        ranked_options: Tuple of ScoredOption objects sorted by score (highest first).
        option_details: Dict mapping option names to their OptionEvaluation details.
        confidence_level: "High", "Medium", or "Low" based on score gap.
        confidence_message: Explanation of the confidence level.
        inputs: The EvaluationInputs that produced this result.
        what_would_change: Tuple of suggestions for what would change the decision.
    
    Properties:
        top_option: Returns the highest-ranked option, or None if no options.
    """
    ranked_options: tuple[ScoredOption, ...]
    option_details: Dict[str, OptionEvaluation]
    confidence_level: ConfidenceLevel
    confidence_message: str
    inputs: EvaluationInputs
    what_would_change: tuple[str, ...]
    
    @property
    def top_option(self) -> Optional[ComputeOption]:
        """Get the top-ranked option.
        
        Returns:
            Optional[ComputeOption]: The highest-ranked option, or None if
                no options are available.
        """
        return self.ranked_options[0].option if self.ranked_options else None

