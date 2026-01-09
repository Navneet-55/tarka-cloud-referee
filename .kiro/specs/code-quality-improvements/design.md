# Design Document: Code Quality Improvements

## Overview

This design outlines refactoring strategies to improve the Tarka codebase quality while preserving all existing functionality. The approach focuses on incremental improvements that enhance maintainability, readability, and testability without changing the system's behavior.

## Architecture

The refactored architecture maintains the existing three-layer structure but with clearer boundaries:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (cli.py, ui.py, rendering.py)         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Business Logic Layer            │
│  (tarka_core.py - evaluation engine)    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Data Model Layer                │
│  (models.py - data structures)          │
└─────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Enhanced Type System

**Current State:** Basic type hints exist but are incomplete.

**Improvements:**
- Add `Literal` types for constrained string values (traffic, control, cost)
- Use `Final` for constants
- Add `TypedDict` for configuration dictionaries
- Use `Protocol` for interface definitions if needed

**Example:**
```python
from typing import Literal, Final

TrafficPattern = Literal["bursty", "steady"]
ControlLevel = Literal["low", "medium", "high"]
CostSensitivity = Literal["sensitive", "flexible"]

# Constants
SCORE_TRAFFIC_MATCH: Final[float] = 2.0
SCORE_CONTROL_MATCH: Final[float] = 2.0
SCORE_COST_MATCH: Final[float] = 1.0
```

### 2. Configuration-Driven Scoring

**Current State:** Scoring rules are hardcoded in conditional logic.

**Improvement:** Extract scoring rules into data structures.

**Design:**
```python
@dataclass(frozen=True)
class ScoringRule:
    """Defines a scoring rule for a compute option."""
    option_name: str
    condition_type: str  # "traffic", "control", "cost"
    condition_value: str  # "bursty", "high", etc.
    points: float
    reason: str

# Scoring rules configuration
SCORING_RULES: Final[List[ScoringRule]] = [
    ScoringRule("AWS Lambda", "traffic", "bursty", 2.0, "Bursty traffic pattern (+2)"),
    ScoringRule("AWS Lambda", "cost", "sensitive", 1.0, "Cost-sensitive workload (+1)"),
    ScoringRule("AWS ECS (Fargate)", "traffic", "steady", 2.0, "Steady traffic pattern (+2)"),
    # ... more rules
]
```

**Benefits:**
- Easier to modify scoring logic
- Testable in isolation
- Self-documenting
- Enables future dynamic rule loading

### 3. Immutable Data Flow

**Current State:** `_score_options` modifies ComputeOption objects in place.

**Improvement:** Use immutable patterns with frozen dataclasses.

**Design:**
```python
@dataclass(frozen=True)
class ComputeOption:
    """Immutable compute option."""
    name: str
    pros: tuple[str, ...]  # Use tuple instead of list
    cons: tuple[str, ...]
    best_for: str

@dataclass(frozen=True)
class ScoredOption:
    """Compute option with score."""
    option: ComputeOption
    score: float
```

**Benefits:**
- Prevents accidental mutations
- Easier to reason about data flow
- Thread-safe by default
- Clearer function contracts

### 4. Functional Decomposition

**Current State:** Some functions are long and do multiple things.

**Improvements:**

**4a. Split `_calculate_score_contributions`:**
```python
def _get_matching_rules(option_name: str, inputs: EvaluationInputs) -> List[ScoringRule]:
    """Get all scoring rules that match the inputs."""
    pass

def _apply_weights(contributions: List[ScoreContribution], weights: Dict[str, float]) -> List[ScoreContribution]:
    """Apply weights to score contributions."""
    pass

def _calculate_score_contributions(option: ComputeOption, inputs: EvaluationInputs) -> List[ScoreContribution]:
    """Calculate score contributions using matching rules."""
    rules = _get_matching_rules(option.name, inputs)
    contributions = [_rule_to_contribution(rule, inputs.weights) for rule in rules]
    return contributions
```

**4b. Simplify `_generate_rationale`:**
```python
def _get_positive_rationale(contributions: List[ScoreContribution]) -> List[str]:
    """Extract positive contribution reasons."""
    return [c.reason for c in contributions if c.points > 0]

def _get_contextual_notes(option: ComputeOption, inputs: EvaluationInputs) -> List[str]:
    """Generate contextual notes about fit."""
    pass

def _generate_rationale(option: ComputeOption, inputs: EvaluationInputs) -> List[str]:
    """Generate complete rationale."""
    contributions = _calculate_score_contributions(option, inputs)
    reasons = _get_positive_rationale(contributions)
    reasons.extend(_get_contextual_notes(option, inputs))
    return reasons if reasons else ["Base score (no specific matches)"]
```

### 5. Error Handling Strategy

**Improvements:**
- Add custom exception classes
- Validate preconditions explicitly
- Provide actionable error messages

**Design:**
```python
class TarkaError(Exception):
    """Base exception for Tarka errors."""
    pass

class InvalidInputError(TarkaError):
    """Raised when inputs are invalid."""
    pass

class ScoringError(TarkaError):
    """Raised when scoring fails."""
    pass

def _validate_inputs(inputs: EvaluationInputs) -> None:
    """Validate evaluation inputs."""
    if not inputs.weights:
        raise InvalidInputError("Weights dictionary cannot be empty")
    
    if any(w < 0 for w in inputs.weights.values()):
        raise InvalidInputError("Weights must be non-negative")
```

### 6. Enhanced Documentation

**Standards:**
- Use Google-style docstrings
- Document all parameters, returns, and raises
- Include examples for public APIs
- Add type information in docstrings

**Example:**
```python
def evaluate(inputs: EvaluationInputs) -> EvaluationResult:
    """
    Evaluate compute options based on workload characteristics.
    
    This function scores AWS compute options (Lambda, ECS/Fargate, EC2)
    based on traffic patterns, control requirements, and cost sensitivity.
    
    Args:
        inputs: Evaluation inputs containing traffic pattern, control level,
            cost sensitivity, and optional weights for each factor.
    
    Returns:
        Complete evaluation result with ranked options, scoring details,
        confidence level, and recommendations.
    
    Raises:
        InvalidInputError: If inputs are invalid or incomplete.
        ScoringError: If scoring calculation fails.
    
    Example:
        >>> inputs = EvaluationInputs(
        ...     traffic="bursty",
        ...     control="low",
        ...     cost="sensitive"
        ... )
        >>> result = evaluate(inputs)
        >>> print(result.top_option.name)
        'AWS Lambda'
    """
    pass
```

## Data Models

### Refactored Models

```python
from dataclasses import dataclass
from typing import Literal, Final

# Type aliases for clarity
TrafficPattern = Literal["bursty", "steady"]
ControlLevel = Literal["low", "medium", "high"]
CostSensitivity = Literal["sensitive", "flexible"]
ConfidenceLevel = Literal["High", "Medium", "Low"]

@dataclass(frozen=True)
class ComputeOption:
    """Immutable compute option with characteristics."""
    name: str
    pros: tuple[str, ...]
    cons: tuple[str, ...]
    best_for: str
    
    @property
    def watch_outs(self) -> tuple[str, ...]:
        """Watch-outs derived from cons."""
        return self.cons

@dataclass(frozen=True)
class EvaluationInputs:
    """Immutable evaluation inputs."""
    traffic: TrafficPattern
    control: ControlLevel
    cost: CostSensitivity
    weights: dict[str, float]
    
    def __post_init__(self):
        """Validate inputs."""
        # Validation logic here
        pass

@dataclass(frozen=True)
class ScoredOption:
    """Compute option with calculated score."""
    option: ComputeOption
    score: float
    contributions: tuple[ScoreContribution, ...]
    rationale: tuple[str, ...]

@dataclass(frozen=True)
class EvaluationResult:
    """Immutable evaluation result."""
    ranked_options: tuple[ScoredOption, ...]
    confidence_level: ConfidenceLevel
    confidence_message: str
    inputs: EvaluationInputs
    what_would_change: tuple[str, ...]
    
    @property
    def top_option(self) -> ScoredOption:
        """Get the top-ranked option."""
        if not self.ranked_options:
            raise ScoringError("No options available")
        return self.ranked_options[0]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Refactoring preserves behavior

*For any* valid EvaluationInputs, the refactored system SHALL produce identical results to the original system (same top option, same scores, same rankings, same confidence level).

**Validates: Requirements 1.1, 2.1, 5.1**

### Property 2: Comprehensive input validation

*For any* invalid input (wrong type, out-of-range value, None where required, or unexpected state), the system SHALL raise an appropriate exception with a non-empty descriptive message.

**Validates: Requirements 1.3, 1.4, 3.1, 3.4**

### Property 3: Input immutability

*For any* input object (ComputeOption, EvaluationInputs, or any collection), calling any function SHALL NOT modify the original object.

**Validates: Requirements 9.2, 9.5**

### Property 4: Internal state isolation

*For any* collection returned by a function, modifying that collection SHALL NOT affect the internal state of the system or subsequent function calls.

**Validates: Requirements 9.3**

### Property 5: Score determinism

*For any* EvaluationInputs, calling evaluate() multiple times SHALL produce identical scores, rankings, and confidence levels.

**Validates: Requirements 7.3**

### Property 6: Documentation completeness

*For any* public function or class in the business logic layer, it SHALL have a docstring that is non-empty.

**Validates: Requirements 4.1**

## Error Handling

### Exception Hierarchy

```python
class TarkaError(Exception):
    """Base exception for all Tarka errors."""
    pass

class InvalidInputError(TarkaError):
    """Raised when inputs fail validation."""
    pass

class ScoringError(TarkaError):
    """Raised when scoring calculation fails."""
    pass

class ConfigurationError(TarkaError):
    """Raised when configuration is invalid."""
    pass
```

### Error Handling Patterns

1. **Validate Early:** Check inputs at function entry
2. **Fail Fast:** Raise exceptions immediately on invalid state
3. **Descriptive Messages:** Include context and expected values
4. **Document Exceptions:** List all exceptions in docstrings

## Testing Strategy

### Unit Testing Approach

**Existing Tests:** Maintain all current tests to ensure behavior preservation.

**New Tests:**
- Test each extracted function independently
- Test error conditions and edge cases
- Test immutability (verify objects aren't modified)
- Test type validation
- Test configuration-driven scoring

**Test Organization:**
```
tests/
  test_core.py          # Existing integration tests
  test_scoring.py       # New: scoring logic tests
  test_models.py        # New: data model tests
  test_validation.py    # New: input validation tests
  test_refactoring.py   # New: behavior preservation tests
```

### Property-Based Testing

Use property-based testing to verify refactoring correctness:

**Test Configuration:**
- Minimum 100 iterations per property test
- Use `hypothesis` library for Python
- Generate random valid inputs
- Compare old vs new behavior

**Key Properties to Test:**
1. Behavior preservation (old system == new system)
2. Immutability (no mutations occur)
3. Determinism (same inputs → same outputs)
4. Type safety (invalid types → exceptions)

### Behavior Preservation Testing

**Critical:** Create a comprehensive test suite that captures current behavior before refactoring.

```python
import hypothesis
from hypothesis import given, strategies as st

@given(
    traffic=st.sampled_from(["bursty", "steady"]),
    control=st.sampled_from(["low", "medium", "high"]),
    cost=st.sampled_from(["sensitive", "flexible"])
)
def test_refactored_matches_original(traffic, control, cost):
    """Refactored system produces identical results to original."""
    inputs = EvaluationInputs(traffic=traffic, control=control, cost=cost)
    
    # Run both implementations
    original_result = original_evaluate(inputs)
    refactored_result = evaluate(inputs)
    
    # Compare results
    assert original_result.top_option.name == refactored_result.top_option.name
    assert original_result.confidence_level == refactored_result.confidence_level
    # ... more assertions
```

## Implementation Strategy

### Phase 1: Add Tests and Constants
1. Create comprehensive behavior preservation tests
2. Extract magic numbers to constants
3. Add missing type hints
4. Verify all tests pass

### Phase 2: Immutability
1. Make dataclasses frozen
2. Change lists to tuples in data models
3. Update functions to avoid mutations
4. Verify behavior preservation tests pass

### Phase 3: Configuration-Driven Scoring
1. Extract scoring rules to data structures
2. Refactor `_calculate_score_contributions` to use rules
3. Verify behavior preservation tests pass

### Phase 4: Functional Decomposition
1. Split large functions into smaller ones
2. Extract repeated logic
3. Verify behavior preservation tests pass

### Phase 5: Error Handling
1. Add custom exception classes
2. Add input validation
3. Add error handling tests

### Phase 6: Documentation
1. Add comprehensive docstrings
2. Add inline comments for complex logic
3. Update README if needed

## Migration Path

**Backward Compatibility:** All public APIs remain unchanged.

**Testing:** Run full test suite after each phase.

**Rollback:** Each phase is independently reversible.

**Validation:** Compare outputs between original and refactored code.
