"""
Data models for Tarka Cloud Compute Referee.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ComputeOption:
    """Represents a compute option with its characteristics."""
    name: str
    pros: List[str]
    cons: List[str]
    best_for: str
    score: float = 0.0
    
    @property
    def watch_outs(self) -> List[str]:
        """Watch-outs are derived from cons."""
        return self.cons.copy()


@dataclass
class EvaluationInputs:
    """Inputs for evaluation."""
    traffic: str  # "bursty" or "steady"
    control: str  # "low", "medium", or "high"
    cost: str  # "sensitive" or "flexible"
    weights: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        """Validate inputs and set defaults."""
        if self.weights is None:
            self.weights = {"traffic": 1.0, "control": 1.0, "cost": 1.0}
        
        # Validate traffic
        if self.traffic not in ["bursty", "steady"]:
            raise ValueError(f"traffic must be 'bursty' or 'steady', got '{self.traffic}'")
        
        # Validate control
        if self.control not in ["low", "medium", "high"]:
            raise ValueError(f"control must be 'low', 'medium', or 'high', got '{self.control}'")
        
        # Validate cost
        if self.cost not in ["sensitive", "flexible"]:
            raise ValueError(f"cost must be 'sensitive' or 'flexible', got '{self.cost}'")


@dataclass
class ScoreContribution:
    """Contribution of a factor to an option's score."""
    factor: str
    points: float
    reason: str


@dataclass
class OptionEvaluation:
    """Evaluation details for a single option."""
    option: ComputeOption
    rank: int
    contributions: List[ScoreContribution]
    rationale: List[str]


@dataclass
class EvaluationResult:
    """Complete evaluation result."""
    ranked_options: List[ComputeOption]
    option_details: Dict[str, OptionEvaluation]
    confidence_level: str
    confidence_message: str
    inputs: EvaluationInputs
    what_would_change: List[str]
    
    @property
    def top_option(self) -> ComputeOption:
        """Get the top-ranked option."""
        return self.ranked_options[0] if self.ranked_options else None

