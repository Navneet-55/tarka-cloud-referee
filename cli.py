"""
Command-line interface for Tarka Cloud Compute Referee.
"""

from typing import Dict, Set
from src.models import EvaluationInputs, EvaluationResult, OptionEvaluation, ComputeOption
from src.tarka_core import evaluate
from src.rendering import format_option_output, format_confidence


def ask(question: str, choices: Dict[str, str]) -> str:
    """Prompt user for input with validation."""
    print(f"\n{question}")
    for key, value in choices.items():
        print(f"{key}: {value}")

    while True:
        answer: str = input("Choose: ").strip().lower()
        if answer in choices:
            return answer
        print("Invalid input. Try again.")


def main() -> None:
    """Main CLI entry point."""
    print("Tarka — Cloud Compute Referee")
    print("=" * 70)

    # Collect inputs
    traffic: str = ask(
        "What best describes your traffic pattern?",
        {"bursty": "Bursty / unpredictable", "steady": "Steady / predictable"}
    )

    control: str = ask(
        "How much infrastructure control do you need?",
        {"low": "Low", "medium": "Medium", "high": "High"}
    )

    cost: str = ask(
        "How cost-sensitive is this workload?",
        {"sensitive": "Very sensitive", "flexible": "Flexible"}
    )

    # Create inputs object
    inputs: EvaluationInputs = EvaluationInputs(traffic=traffic, control=control, cost=cost)
    
    # Evaluate
    result: EvaluationResult = evaluate(inputs)

    # Display results
    print("\n" + "=" * 70)
    print("INPUT SUMMARY")
    print("=" * 70)
    print(f"Traffic pattern: {traffic}")
    print(f"Infrastructure control: {control}")
    print(f"Cost sensitivity: {cost}")
    print("=" * 70)

    # Confidence
    print(f"\n{'=' * 70}")
    print(format_confidence(result.confidence_level, result.confidence_message))
    print("=" * 70)

    # Ranked options
    print("\nRecommended options (ranked):")
    for opt in result.ranked_options:
        evaluation: OptionEvaluation = result.option_details[opt.name]
        print(f"\n{'=' * 70}")
        print(f"{evaluation.rank}. {opt.name}")
        print("=" * 70)
        print(format_option_output(opt, evaluation))
    
    # Explainability timeline for top option
    if result.ranked_options:
        top_opt: ComputeOption = result.top_option
        top_eval: OptionEvaluation = result.option_details[top_opt.name]
        print(f"\n{'=' * 70}")
        print(f"EXPLAINABILITY TIMELINE (Top Option: {top_opt.name})")
        print("=" * 70)
        print("Step-by-step scoring breakdown:")
        
        for contrib in top_eval.contributions:
            print(f"  {contrib.factor.capitalize()}: {contrib.reason}")
            print(f"    → Score contribution: +{contrib.points:.1f}")
        
        # Show factors with no contribution
        all_factors: Set[str] = {"traffic", "control", "cost"}
        contributing_factors: Set[str] = {c.factor for c in top_eval.contributions}
        for factor in all_factors - contributing_factors:
            print(f"  {factor.capitalize()}: No contribution to score")
    
    # What would change
    if result.what_would_change:
        print(f"\n{'=' * 70}")
        print("WHAT WOULD CHANGE THIS DECISION?")
        print("=" * 70)
        for suggestion in result.what_would_change:
            print(f"  • {suggestion}")
    
    # Final disclaimer
    print("\n" + "=" * 70)
    print("Note: This is not a single best answer; use the trade-offs above to decide.")
    print("=" * 70)


if __name__ == "__main__":
    main()
