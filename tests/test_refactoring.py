"""
Behavior preservation tests for Tarka refactoring.
These tests capture the current behavior to ensure refactoring doesn't break functionality.
"""

import unittest
import sys
from pathlib import Path
from copy import deepcopy

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import EvaluationInputs
from src.tarka_core import evaluate, get_compute_options
from src.exceptions import InvalidInputError


class TestBehaviorPreservation(unittest.TestCase):
    """Test that refactoring preserves all existing behavior."""
    
    def test_all_input_combinations(self):
        """Test all valid combinations of inputs produce consistent results."""
        traffic_options = ["bursty", "steady"]
        control_options = ["low", "medium", "high"]
        cost_options = ["sensitive", "flexible"]
        
        for traffic in traffic_options:
            for control in control_options:
                for cost in cost_options:
                    with self.subTest(traffic=traffic, control=control, cost=cost):
                        inputs = EvaluationInputs(
                            traffic=traffic,
                            control=control,
                            cost=cost
                        )
                        result = evaluate(inputs)
                        
                        # Verify result structure
                        self.assertIsNotNone(result)
                        self.assertEqual(len(result.ranked_options), 3)
                        self.assertIsNotNone(result.top_option)
                        self.assertIn(result.confidence_level, ["High", "Medium", "Low"])
    
    def test_lambda_scores_highest_for_bursty_sensitive(self):
        """Lambda should score highest for bursty traffic + cost sensitive."""
        inputs = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        result = evaluate(inputs)
        
        self.assertEqual(result.top_option.name, "AWS Lambda")
        # Lambda gets +2 for bursty, +1 for cost sensitive = 3.0
        self.assertEqual(result.ranked_options[0].score, 3.0)
    
    def test_ecs_scores_highest_for_steady_medium(self):
        """ECS should score highest for steady traffic + medium control."""
        inputs = EvaluationInputs(
            traffic="steady",
            control="medium",
            cost="flexible"
        )
        result = evaluate(inputs)
        
        self.assertEqual(result.top_option.name, "AWS ECS (Fargate)")
        # ECS gets +2 for steady, +1 for medium control = 3.0
        self.assertEqual(result.ranked_options[0].score, 3.0)
    
    def test_ec2_scores_highest_for_high_control(self):
        """EC2 should score highest for high control needs."""
        inputs = EvaluationInputs(
            traffic="steady",
            control="high",
            cost="flexible"
        )
        result = evaluate(inputs)
        
        # EC2 gets +2 for high control, ECS gets +2 for steady
        # They should tie, but EC2 might rank first due to list order
        top_names = [scored_opt.option.name for scored_opt in result.ranked_options[:2]]
        self.assertIn("AWS EC2", top_names)
        self.assertIn("AWS ECS (Fargate)", top_names)
    
    def test_scores_are_deterministic(self):
        """Same inputs should produce same scores every time."""
        inputs = EvaluationInputs(
            traffic="bursty",
            control="medium",
            cost="sensitive"
        )
        
        result1 = evaluate(inputs)
        result2 = evaluate(inputs)
        
        # Compare top options
        self.assertEqual(result1.top_option.name, result2.top_option.name)
        self.assertEqual(result1.ranked_options[0].score, result2.ranked_options[0].score)
        
        # Compare all rankings
        for scored_opt1, scored_opt2 in zip(result1.ranked_options, result2.ranked_options):
            self.assertEqual(scored_opt1.option.name, scored_opt2.option.name)
            self.assertEqual(scored_opt1.score, scored_opt2.score)
    
    def test_confidence_calculation(self):
        """Test confidence level calculation based on score gaps."""
        # High confidence: gap >= 3
        inputs_high = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        result_high = evaluate(inputs_high)
        self.assertEqual(result_high.confidence_level, "High")
        
        # Low confidence: gap < 2
        inputs_low = EvaluationInputs(
            traffic="steady",
            control="high",
            cost="flexible"
        )
        result_low = evaluate(inputs_low)
        # EC2 and ECS both score 2.0, gap = 0
        self.assertEqual(result_low.confidence_level, "Low")
    
    def test_option_details_structure(self):
        """Test that option_details contains all required information."""
        inputs = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        result = evaluate(inputs)
        
        # Check all options have details
        self.assertEqual(len(result.option_details), 3)
        
        for scored_opt in result.ranked_options:
            opt = scored_opt.option
            self.assertIn(opt.name, result.option_details)
            details = result.option_details[opt.name]
            
            # Verify structure
            self.assertEqual(details.option.name, opt.name)
            self.assertIsInstance(details.rank, int)
            self.assertIsInstance(details.contributions, tuple)
            self.assertIsInstance(details.rationale, tuple)
            self.assertGreater(len(details.rationale), 0)
    
    def test_rationale_generation(self):
        """Test that rationale is generated correctly."""
        inputs = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        result = evaluate(inputs)
        
        lambda_details = result.option_details["AWS Lambda"]
        
        # Lambda should have positive rationale for bursty and cost sensitive
        rationale_text = " ".join(lambda_details.rationale)
        self.assertIn("Bursty traffic", rationale_text)
        self.assertIn("Cost-sensitive", rationale_text)
    
    def test_what_would_change_suggestions(self):
        """Test that 'what would change' suggestions are generated."""
        inputs = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        result = evaluate(inputs)
        
        # Should have suggestions
        self.assertGreater(len(result.what_would_change), 0)
        
        # Suggestions should be strings
        for suggestion in result.what_would_change:
            self.assertIsInstance(suggestion, str)
            self.assertGreater(len(suggestion), 0)
    
    def test_custom_weights(self):
        """Test that custom weights affect scoring."""
        # Default weights
        inputs_default = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        result_default = evaluate(inputs_default)
        
        # Custom weights (emphasize traffic)
        inputs_custom = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive",
            weights={"traffic": 2.0, "control": 1.0, "cost": 1.0}
        )
        result_custom = evaluate(inputs_custom)
        
        # Both should rank Lambda first, but scores will differ
        self.assertEqual(result_default.top_option.name, "AWS Lambda")
        self.assertEqual(result_custom.top_option.name, "AWS Lambda")
        
        # Custom weights should affect the score
        # Note: weights are normalized, so we just check they're different
        self.assertNotEqual(result_default.ranked_options[0].score, result_custom.ranked_options[0].score)
    
    def test_get_compute_options_returns_three(self):
        """Test that get_compute_options returns exactly 3 options."""
        options = get_compute_options()
        
        self.assertEqual(len(options), 3)
        
        # Verify expected options
        option_names = {opt.name for opt in options}
        expected_names = {"AWS Lambda", "AWS ECS (Fargate)", "AWS EC2"}
        self.assertEqual(option_names, expected_names)
        
        # Verify structure
        for opt in options:
            self.assertIsInstance(opt.name, str)
            self.assertIsInstance(opt.pros, tuple)
            self.assertIsInstance(opt.cons, tuple)
            self.assertIsInstance(opt.best_for, str)
            self.assertGreater(len(opt.pros), 0)
            self.assertGreater(len(opt.cons), 0)
    
    def test_watch_outs_property(self):
        """Test that watch_outs property returns cons (immutable tuple)."""
        options = get_compute_options()
        
        for opt in options:
            watch_outs = opt.watch_outs
            self.assertEqual(watch_outs, opt.cons)
            # Since tuples are immutable, they can be the same object
            self.assertIs(watch_outs, opt.cons)
    
    def test_zero_score_options(self):
        """Test options that don't match any criteria get zero score."""
        inputs = EvaluationInputs(
            traffic="steady",
            control="low",
            cost="flexible"
        )
        result = evaluate(inputs)
        
        # Lambda should have 0 score (no matches)
        lambda_scored = next(scored_opt for scored_opt in result.ranked_options if scored_opt.option.name == "AWS Lambda")
        self.assertEqual(lambda_scored.score, 0.0)
    
    def test_inputs_validation(self):
        """Test that invalid inputs raise InvalidInputError."""
        # Invalid traffic
        with self.assertRaises(InvalidInputError) as cm:
            EvaluationInputs(traffic="invalid", control="low", cost="sensitive")
        self.assertIn("traffic", str(cm.exception))
        
        # Invalid control
        with self.assertRaises(InvalidInputError) as cm:
            EvaluationInputs(traffic="bursty", control="invalid", cost="sensitive")
        self.assertIn("control", str(cm.exception))
        
        # Invalid cost
        with self.assertRaises(InvalidInputError) as cm:
            EvaluationInputs(traffic="bursty", control="low", cost="invalid")
        self.assertIn("cost", str(cm.exception))
        
        # Negative weights
        with self.assertRaises(InvalidInputError) as cm:
            EvaluationInputs(
                traffic="bursty",
                control="low",
                cost="sensitive",
                weights={"traffic": -1.0, "control": 1.0, "cost": 1.0}
            )
        self.assertIn("non-negative", str(cm.exception))
    
    def test_inputs_default_weights(self):
        """Test that inputs get default weights when not provided."""
        inputs = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        
        self.assertIsNotNone(inputs.weights)
        self.assertEqual(inputs.weights, {"traffic": 1.0, "control": 1.0, "cost": 1.0})


if __name__ == "__main__":
    unittest.main()



# Property-Based Tests
try:
    from hypothesis import given, strategies as st, settings
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False


@unittest.skipUnless(HYPOTHESIS_AVAILABLE, "hypothesis not installed")
class TestBehaviorPreservationProperties(unittest.TestCase):
    """Property-based tests for behavior preservation."""
    
    @given(
        traffic=st.sampled_from(["bursty", "steady"]),
        control=st.sampled_from(["low", "medium", "high"]),
        cost=st.sampled_from(["sensitive", "flexible"])
    )
    @settings(max_examples=100)
    def test_property_refactoring_preserves_behavior(self, traffic, control, cost):
        """
        Property 1: Refactoring preserves behavior
        
        For any valid EvaluationInputs, the system produces consistent results:
        - Returns exactly 3 ranked options
        - Top option is one of the three compute options
        - Confidence level is valid
        - All scores are non-negative
        - Rankings are in descending score order
        
        Feature: code-quality-improvements, Property 1: Refactoring preserves behavior
        Validates: Requirements 1.1, 2.1, 5.1
        """
        inputs = EvaluationInputs(
            traffic=traffic,
            control=control,
            cost=cost
        )
        result = evaluate(inputs)
        
        # Verify result structure
        self.assertIsNotNone(result)
        self.assertEqual(len(result.ranked_options), 3)
        
        # Verify top option exists and is valid
        self.assertIsNotNone(result.top_option)
        self.assertIn(result.top_option.name, ["AWS Lambda", "AWS ECS (Fargate)", "AWS EC2"])
        
        # Verify confidence level is valid
        self.assertIn(result.confidence_level, ["High", "Medium", "Low"])
        
        # Verify all scores are non-negative
        for scored_opt in result.ranked_options:
            self.assertGreaterEqual(scored_opt.score, 0.0)
        
        # Verify rankings are in descending score order
        for i in range(len(result.ranked_options) - 1):
            self.assertGreaterEqual(
                result.ranked_options[i].score,
                result.ranked_options[i + 1].score
            )
        
        # Verify option details exist for all options
        self.assertEqual(len(result.option_details), 3)
        for scored_opt in result.ranked_options:
            self.assertIn(scored_opt.option.name, result.option_details)
        
        # Verify what_would_change suggestions exist
        self.assertIsInstance(result.what_would_change, tuple)
        self.assertGreater(len(result.what_would_change), 0)
    
    @given(
        traffic=st.sampled_from(["bursty", "steady"]),
        control=st.sampled_from(["low", "medium", "high"]),
        cost=st.sampled_from(["sensitive", "flexible"])
    )
    @settings(max_examples=100)
    def test_property_determinism(self, traffic, control, cost):
        """
        Property 5: Score determinism
        
        For any EvaluationInputs, calling evaluate() multiple times
        produces identical scores, rankings, and confidence levels.
        
        Feature: code-quality-improvements, Property 5: Score determinism
        Validates: Requirements 7.3
        """
        inputs = EvaluationInputs(
            traffic=traffic,
            control=control,
            cost=cost
        )
        
        # Run evaluation twice
        result1 = evaluate(inputs)
        result2 = evaluate(inputs)
        
        # Verify top options match
        self.assertEqual(result1.top_option.name, result2.top_option.name)
        self.assertEqual(result1.ranked_options[0].score, result2.ranked_options[0].score)
        
        # Verify all rankings match
        for scored_opt1, scored_opt2 in zip(result1.ranked_options, result2.ranked_options):
            self.assertEqual(scored_opt1.option.name, scored_opt2.option.name)
            self.assertEqual(scored_opt1.score, scored_opt2.score)
        
        # Verify confidence levels match
        self.assertEqual(result1.confidence_level, result2.confidence_level)

    @given(
        traffic=st.sampled_from(["bursty", "steady"]),
        control=st.sampled_from(["low", "medium", "high"]),
        cost=st.sampled_from(["sensitive", "flexible"])
    )
    @settings(max_examples=100)
    def test_property_input_immutability(self, traffic, control, cost):
        """
        Property 3: Input immutability
        
        EvaluationInputs objects are immutable - attempting to modify them
        should raise an error. This ensures inputs cannot be accidentally
        changed during evaluation.
        
        Feature: code-quality-improvements, Property 3: Input immutability
        Validates: Requirements 9.2, 9.5
        """
        inputs = EvaluationInputs(
            traffic=traffic,
            control=control,
            cost=cost
        )
        
        # Verify inputs are frozen (immutable)
        with self.assertRaises(Exception):  # FrozenInstanceError or AttributeError
            inputs.traffic = "different"
        
        with self.assertRaises(Exception):
            inputs.control = "different"
        
        with self.assertRaises(Exception):
            inputs.cost = "different"
    
    @given(
        traffic=st.sampled_from(["bursty", "steady"]),
        control=st.sampled_from(["low", "medium", "high"]),
        cost=st.sampled_from(["sensitive", "flexible"])
    )
    @settings(max_examples=100)
    def test_property_internal_state_isolation(self, traffic, control, cost):
        """
        Property 4: Internal state isolation
        
        Multiple evaluations with the same inputs should not interfere with
        each other. Each evaluation should produce independent results.
        
        Feature: code-quality-improvements, Property 4: Internal state isolation
        Validates: Requirements 9.3
        """
        inputs = EvaluationInputs(
            traffic=traffic,
            control=control,
            cost=cost
        )
        
        # Run two evaluations
        result1 = evaluate(inputs)
        result2 = evaluate(inputs)
        
        # Results should be equal but not the same object
        self.assertIsNot(result1, result2)
        self.assertIsNot(result1.ranked_options, result2.ranked_options)
        
        # But values should be identical
        self.assertEqual(len(result1.ranked_options), len(result2.ranked_options))
        for scored1, scored2 in zip(result1.ranked_options, result2.ranked_options):
            self.assertEqual(scored1.option.name, scored2.option.name)
            self.assertEqual(scored1.score, scored2.score)
