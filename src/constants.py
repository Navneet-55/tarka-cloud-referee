"""
Constants and type aliases for Tarka Cloud Compute Referee.
"""

from typing import Literal, Final

# Type aliases for constrained string values
TrafficPattern = Literal["bursty", "steady"]
ControlLevel = Literal["low", "medium", "high"]
CostSensitivity = Literal["sensitive", "flexible"]
ConfidenceLevel = Literal["High", "Medium", "Low"]

# Scoring constants
SCORE_TRAFFIC_MATCH: Final[float] = 2.0
SCORE_CONTROL_HIGH_MATCH: Final[float] = 2.0
SCORE_CONTROL_MEDIUM_MATCH: Final[float] = 1.0
SCORE_COST_MATCH: Final[float] = 1.0

# Confidence threshold constants
CONFIDENCE_HIGH_THRESHOLD: Final[float] = 3.0
CONFIDENCE_MEDIUM_THRESHOLD: Final[float] = 2.0

# Default weights
DEFAULT_WEIGHTS: Final[dict[str, float]] = {
    "traffic": 1.0,
    "control": 1.0,
    "cost": 1.0
}

# Valid input values
VALID_TRAFFIC_PATTERNS: Final[tuple[str, ...]] = ("bursty", "steady")
VALID_CONTROL_LEVELS: Final[tuple[str, ...]] = ("low", "medium", "high")
VALID_COST_SENSITIVITIES: Final[tuple[str, ...]] = ("sensitive", "flexible")

# Compute option names
OPTION_LAMBDA: Final[str] = "AWS Lambda"
OPTION_ECS: Final[str] = "AWS ECS (Fargate)"
OPTION_EC2: Final[str] = "AWS EC2"
