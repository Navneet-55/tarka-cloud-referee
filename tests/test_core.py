"""
Unit tests for Tarka core evaluation logic.
Uses only standard library (unittest).
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import EvaluationInputs
from src.tarka_core import evaluate, get_compute_options


class TestCoreEvaluation(unittest.TestCase):
    """Test core evaluation logic."""
    
    def test_bursty_low_control_ranks_lambda_first(self):
        """Bursty traffic + low control should rank Lambda first."""
        inputs = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        result = evaluate(inputs)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result.ranked_options), 0)
        self.assertEqual(result.ranked_options[0].option.name, "AWS Lambda")
        self.assertGreater(result.ranked_options[0].score, 0)
    
    def test_steady_high_control_improves_ec2_ranking(self):
        """Steady traffic + high control should improve EC2 ranking."""
        inputs = EvaluationInputs(
            traffic="steady",
            control="high",
            cost="flexible"
        )
        result = evaluate(inputs)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result.ranked_options), 3)
        
        # EC2 should be ranked in top 2 due to high control (+2 points)
        # ECS also gets +2 for steady traffic, so they may tie
        ec2_rank = next((i+1 for i, scored_opt in enumerate(result.ranked_options) if scored_opt.option.name == "AWS EC2"), None)
        self.assertIsNotNone(ec2_rank)
        self.assertLessEqual(ec2_rank, 2)  # EC2 should be in top 2
        
        # Verify EC2 has a positive score
        ec2_scored = next(scored_opt for scored_opt in result.ranked_options if scored_opt.option.name == "AWS EC2")
        self.assertGreater(ec2_scored.score, 0)
    
    def test_medium_control_steady_returns_three_options(self):
        """Medium control + steady traffic should return all 3 options without crashing."""
        inputs = EvaluationInputs(
            traffic="steady",
            control="medium",
            cost="flexible"
        )
        result = evaluate(inputs)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result.ranked_options), 3)
        
        # Verify all expected options are present
        option_names = {scored_opt.option.name for scored_opt in result.ranked_options}
        expected_names = {"AWS Lambda", "AWS ECS (Fargate)", "AWS EC2"}
        self.assertEqual(option_names, expected_names)
        
        # Verify each option has evaluation details
        for scored_opt in result.ranked_options:
            opt = scored_opt.option
            self.assertIn(opt.name, result.option_details)
            eval_detail = result.option_details[opt.name]
            self.assertEqual(eval_detail.option.name, opt.name)
            self.assertGreaterEqual(eval_detail.rank, 1)
            self.assertLessEqual(eval_detail.rank, 3)
    
    def test_evaluation_result_structure(self):
        """Verify evaluation result has all required fields."""
        inputs = EvaluationInputs(
            traffic="bursty",
            control="low",
            cost="sensitive"
        )
        result = evaluate(inputs)
        
        # Check result structure
        self.assertIsNotNone(result.ranked_options)
        self.assertIsNotNone(result.option_details)
        self.assertIsNotNone(result.confidence_level)
        self.assertIsNotNone(result.confidence_message)
        self.assertIsNotNone(result.inputs)
        self.assertIsNotNone(result.what_would_change)
        
        # Check confidence level is valid
        self.assertIn(result.confidence_level, ["High", "Medium", "Low"])
        
        # Check top option exists
        self.assertIsNotNone(result.top_option)
        self.assertEqual(result.top_option, result.ranked_options[0].option)


if __name__ == "__main__":
    unittest.main()

