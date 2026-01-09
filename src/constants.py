"""
Constants and type aliases for Tarka Cloud Compute Referee.

This module defines all constants, type aliases, and configuration used
throughout the application. It includes scoring rules, thresholds, and
valid input values.
"""

from dataclasses import dataclass
from typing import Literal, Final

# Type aliases for constrained string values
TrafficPattern = Literal["bursty", "steady"]
"""Traffic pattern type: 'bursty' for unpredictable spikes, 'steady' for consistent load."""

ControlLevel = Literal["low", "medium", "high"]
"""Infrastructure control level: 'low' for managed, 'medium' for balanced, 'high' for full control."""

CostSensitivity = Literal["sensitive", "flexible"]
"""Cost sensitivity: 'sensitive' for cost-conscious, 'flexible' for less constrained."""

ConfidenceLevel = Literal["High", "Medium", "Low"]
"""Confidence level in the recommendation based on score gap."""


@dataclass(frozen=True)
class ScoringRule:
    """A rule for scoring compute options based on input conditions.
    
    Attributes:
        option_name: The name of the compute option this rule applies to.
        condition_type: The type of condition ("traffic", "control", or "cost").
        condition_value: The value that triggers this rule (e.g., "bursty", "high").
        points: The number of points to award when this rule matches.
        reason: Human-readable explanation of why points are awarded.
    """
    option_name: str
    condition_type: str  # "traffic", "control", or "cost"
    condition_value: str  # The value that triggers this rule
    points: float
    reason: str

# Scoring constants
SCORE_TRAFFIC_MATCH: Final[float] = 2.0
"""Points awarded when traffic pattern matches option's strength."""

SCORE_CONTROL_HIGH_MATCH: Final[float] = 2.0
"""Points awarded when high control requirement matches EC2."""

SCORE_CONTROL_MEDIUM_MATCH: Final[float] = 1.0
"""Points awarded when medium control requirement matches ECS."""

SCORE_COST_MATCH: Final[float] = 1.0
"""Points awarded when cost sensitivity matches Lambda's pay-per-use model."""

# Confidence threshold constants
CONFIDENCE_HIGH_THRESHOLD: Final[float] = 3.0
"""Score gap threshold for high confidence (gap >= 3.0)."""

CONFIDENCE_MEDIUM_THRESHOLD: Final[float] = 2.0
"""Score gap threshold for medium confidence (2.0 <= gap < 3.0)."""

# Default weights
DEFAULT_WEIGHTS: Final[dict[str, float]] = {
    "traffic": 1.0,
    "control": 1.0,
    "cost": 1.0
}
"""Default weights for each factor when not specified by user."""

# Valid input values
VALID_TRAFFIC_PATTERNS: Final[tuple[str, ...]] = ("bursty", "steady")
"""Valid traffic pattern values."""

VALID_CONTROL_LEVELS: Final[tuple[str, ...]] = ("low", "medium", "high")
"""Valid infrastructure control level values."""

VALID_COST_SENSITIVITIES: Final[tuple[str, ...]] = ("sensitive", "flexible")
"""Valid cost sensitivity values."""

# Compute option names
OPTION_LAMBDA: Final[str] = "AWS Lambda"
"""Name constant for AWS Lambda option."""

OPTION_ECS: Final[str] = "AWS ECS (Fargate)"
"""Name constant for AWS ECS (Fargate) option."""

OPTION_EC2: Final[str] = "AWS EC2"
"""Name constant for AWS EC2 option."""

# Scoring rules configuration
SCORING_RULES: Final[tuple[ScoringRule, ...]] = (
    # Lambda rules
    ScoringRule(
        option_name=OPTION_LAMBDA,
        condition_type="traffic",
        condition_value="bursty",
        points=SCORE_TRAFFIC_MATCH,
        reason=f"Bursty traffic pattern (+{int(SCORE_TRAFFIC_MATCH)})"
    ),
    ScoringRule(
        option_name=OPTION_LAMBDA,
        condition_type="cost",
        condition_value="sensitive",
        points=SCORE_COST_MATCH,
        reason=f"Cost-sensitive workload (+{int(SCORE_COST_MATCH)})"
    ),
    # ECS rules
    ScoringRule(
        option_name=OPTION_ECS,
        condition_type="traffic",
        condition_value="steady",
        points=SCORE_TRAFFIC_MATCH,
        reason=f"Steady traffic pattern (+{int(SCORE_TRAFFIC_MATCH)})"
    ),
    ScoringRule(
        option_name=OPTION_ECS,
        condition_type="control",
        condition_value="medium",
        points=SCORE_CONTROL_MEDIUM_MATCH,
        reason=f"Medium control requirement (+{int(SCORE_CONTROL_MEDIUM_MATCH)})"
    ),
    # EC2 rules
    ScoringRule(
        option_name=OPTION_EC2,
        condition_type="control",
        condition_value="high",
        points=SCORE_CONTROL_HIGH_MATCH,
        reason=f"High control requirement (+{int(SCORE_CONTROL_HIGH_MATCH)})"
    ),
)
"""
Configuration of all scoring rules.

Each rule specifies:
- Which option it applies to
- What condition must be met (traffic/control/cost and its value)
- How many points to award
- The reason for awarding points

Rules are evaluated for each option during scoring, and matching rules
contribute their points (weighted by user preferences) to the option's total score.
"""
