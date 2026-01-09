# Implementation Plan: Code Quality Improvements

## Overview

This plan refactors the Tarka codebase to improve code quality while preserving all existing functionality. Each task includes behavior preservation verification to ensure no regressions.

## Tasks

- [x] 1. Create behavior preservation test suite
  - Create `tests/test_refactoring.py` with comprehensive tests
  - Capture current behavior of all public functions
  - Test all input combinations (traffic, control, cost)
  - Verify scores, rankings, and confidence levels
  - _Requirements: 1.1, 2.1, 5.1_

- [x] 1.1 Write property test for behavior preservation
  - **Property 1: Refactoring preserves behavior**
  - **Validates: Requirements 1.1, 2.1, 5.1**

- [x] 2. Extract constants and add type aliases
  - [x] 2.1 Create `src/constants.py` module
    - Define scoring point constants (SCORE_TRAFFIC_MATCH, etc.)
    - Define confidence threshold constants
    - Define type aliases (TrafficPattern, ControlLevel, CostSensitivity)
    - _Requirements: 2.2, 1.5_
  
  - [x] 2.2 Update `src/models.py` to use type aliases
    - Import and use Literal types for constrained strings
    - Update EvaluationInputs to use type aliases
    - _Requirements: 1.1, 1.2, 1.5_
  
  - [x] 2.3 Update `src/tarka_core.py` to use constants
    - Replace magic numbers with named constants
    - Import constants from constants module
    - _Requirements: 2.2_
  
  - [x] 2.4 Run behavior preservation tests
    - Verify all tests pass after constant extraction
    - _Requirements: 1.1, 2.1_

- [-] 3. Add comprehensive type hints
  - [ ] 3.1 Add missing type hints to `src/tarka_core.py`
    - Add return type hints to all functions
    - Add parameter type hints to all functions
    - Use typing module features (List, Dict, Tuple, Optional)
    - _Requirements: 1.1, 1.2_
  
  - [ ] 3.2 Add missing type hints to `src/rendering.py`
    - Add type hints to all functions
    - _Requirements: 1.1_
  
  - [ ] 3.3 Add missing type hints to `cli.py`
    - Add type hints to all functions
    - _Requirements: 1.1_
  
  - [ ] 3.4 Run type checker (mypy)
    - Verify no type errors
    - _Requirements: 1.1, 1.2_

- [ ] 4. Implement immutable data models
  - [ ] 4.1 Make ComputeOption immutable
    - Add `frozen=True` to dataclass decorator
    - Change `pros` and `cons` from List to tuple
    - Update `watch_outs` property to return tuple
    - _Requirements: 9.1, 9.2_
  
  - [ ] 4.2 Make EvaluationInputs immutable
    - Add `frozen=True` to dataclass decorator
    - Update validation in `__post_init__`
    - _Requirements: 9.1, 9.2_
  
  - [ ] 4.3 Create ScoredOption dataclass
    - Define frozen dataclass with option, score, contributions, rationale
    - Use tuples for collections
    - _Requirements: 9.1_
  
  - [ ] 4.4 Update EvaluationResult to use tuples
    - Change ranked_options from List to tuple
    - Change what_would_change from List to tuple
    - Update top_option property to handle empty tuple
    - _Requirements: 9.1, 9.3_
  
  - [ ] 4.5 Update `get_compute_options()` to return tuple
    - Change return type from List to tuple
    - Update function to return tuple of ComputeOptions
    - _Requirements: 9.1_
  
  - [ ] 4.6 Write property test for input immutability
    - **Property 3: Input immutability**
    - **Validates: Requirements 9.2, 9.5**
  
  - [ ] 4.7 Write property test for internal state isolation
    - **Property 4: Internal state isolation**
    - **Validates: Requirements 9.3**
  
  - [ ] 4.8 Run behavior preservation tests
    - Verify all tests pass after immutability changes
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 5. Refactor scoring to be configuration-driven
  - [ ] 5.1 Create ScoringRule dataclass in `src/constants.py`
    - Define frozen dataclass with option_name, condition_type, condition_value, points, reason
    - _Requirements: 5.2, 5.4_
  
  - [ ] 5.2 Define SCORING_RULES configuration
    - Extract all scoring rules from conditional logic
    - Create list of ScoringRule objects
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [ ] 5.3 Refactor `_calculate_score_contributions()`
    - Create `_get_matching_rules()` helper function
    - Update to use SCORING_RULES configuration
    - Remove hardcoded conditional logic
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [ ] 5.4 Run behavior preservation tests
    - Verify scores remain identical after refactoring
    - _Requirements: 5.1, 5.2, 5.4_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Decompose large functions
  - [ ] 7.1 Split `_generate_rationale()` into smaller functions
    - Create `_get_positive_rationale()` helper
    - Create `_get_contextual_notes()` helper
    - Refactor main function to use helpers
    - _Requirements: 2.4, 5.1_
  
  - [ ] 7.2 Split `_get_what_would_change()` into smaller functions
    - Extract per-option logic into separate functions
    - Create data-driven approach if possible
    - _Requirements: 2.4, 5.1_
  
  - [ ] 7.3 Refactor `_score_options()` to avoid mutation
    - Create new ScoredOption objects instead of modifying ComputeOption
    - Return tuple of ScoredOption objects
    - Update callers to use ScoredOption
    - _Requirements: 9.2, 9.5_
  
  - [ ] 7.4 Run behavior preservation tests
    - Verify all tests pass after decomposition
    - _Requirements: 2.4, 5.1_

- [ ] 8. Add custom exception classes
  - [ ] 8.1 Create `src/exceptions.py` module
    - Define TarkaError base exception
    - Define InvalidInputError exception
    - Define ScoringError exception
    - Define ConfigurationError exception
    - _Requirements: 3.1, 3.4_
  
  - [ ] 8.2 Add input validation to EvaluationInputs
    - Validate weights are non-negative
    - Validate weights dict is not empty
    - Raise InvalidInputError with descriptive messages
    - _Requirements: 1.4, 3.1_
  
  - [ ] 8.3 Add error handling to `evaluate()`
    - Validate inputs at function entry
    - Handle empty options list
    - Raise appropriate exceptions
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [ ] 8.4 Update `top_option` property error handling
    - Raise ScoringError if no options available
    - _Requirements: 3.2, 3.4_
  
  - [ ] 8.5 Write property test for input validation
    - **Property 2: Comprehensive input validation**
    - **Validates: Requirements 1.3, 1.4, 3.1, 3.4**
  
  - [ ] 8.6 Write unit tests for edge cases
    - Test empty weights dict
    - Test negative weights
    - Test None values
    - _Requirements: 3.2_

- [ ] 9. Add comprehensive docstrings
  - [ ] 9.1 Add docstrings to `src/tarka_core.py`
    - Add Google-style docstrings to all public functions
    - Document parameters, returns, and raises
    - Add examples to `evaluate()` function
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ] 9.2 Add docstrings to `src/models.py`
    - Add docstrings to all dataclasses
    - Document attributes and properties
    - _Requirements: 4.1, 4.2_
  
  - [ ] 9.3 Add docstrings to `src/rendering.py`
    - Add docstrings to all functions
    - _Requirements: 4.1, 4.2_
  
  - [ ] 9.4 Add docstrings to `src/constants.py`
    - Document constants and type aliases
    - _Requirements: 4.1, 4.5_
  
  - [ ] 9.5 Write property test for documentation completeness
    - **Property 6: Documentation completeness**
    - **Validates: Requirements 4.1**

- [ ] 10. Add determinism tests
  - [ ] 10.1 Write property test for score determinism
    - **Property 5: Score determinism**
    - **Validates: Requirements 7.3**

- [ ] 11. Update existing tests
  - [ ] 11.1 Update `tests/test_core.py` for new data structures
    - Update tests to work with ScoredOption
    - Update tests to work with tuples instead of lists
    - Ensure all existing tests still pass
    - _Requirements: 9.1, 9.2_
  
  - [ ] 11.2 Add inline comments to complex logic
    - Add comments explaining scoring algorithm
    - Add comments explaining confidence calculation
    - Document design decisions
    - _Requirements: 4.5_

- [ ] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Behavior preservation tests run after each major change
- Property tests validate correctness properties across many inputs
- Unit tests validate specific examples and edge cases
- All refactoring maintains backward compatibility
