from src.tarka_core import (
    get_compute_options, score_options, get_score_rationale,
    evaluate, get_confidence, get_what_would_change, get_assumptions
)


def ask(question, choices):
    print(f"\n{question}")
    for key, value in choices.items():
        print(f"{key}: {value}")

    while True:
        answer = input("Choose: ").strip().lower()
        if answer in choices:
            return answer
        print("Invalid input. Try again.")


def main():
    print("Tarka — Cloud Compute Referee")

    traffic = ask(
        "What best describes your traffic pattern?",
        {"bursty": "Bursty / unpredictable", "steady": "Steady / predictable"}
    )

    control = ask(
        "How much infrastructure control do you need?",
        {"low": "Low", "medium": "Medium", "high": "High"}
    )

    cost = ask(
        "How cost-sensitive is this workload?",
        {"sensitive": "Very sensitive", "flexible": "Flexible"}
    )

    ranked, details = evaluate(traffic, control, cost)
    
    # Calculate confidence
    conf_level, conf_msg = get_confidence(ranked)
    
    print("\n" + "="*70)
    print("INPUT SUMMARY")
    print("="*70)
    print(f"Traffic pattern: {traffic}")
    print(f"Infrastructure control: {control}")
    print(f"Cost sensitivity: {cost}")
    print("="*70)
    
    print(f"\n{'='*70}")
    print(f"CONFIDENCE / SENSITIVITY: {conf_level.upper()}")
    print(f"{'='*70}")
    print(f"{conf_msg}")

    print("\nRecommended options (ranked):")
    for idx, opt in enumerate(ranked, 1):
        print(f"\n{'='*70}")
        print(f"{idx}. {opt.name}")
        print(f"{'='*70}")
        print(f"Score: {opt.score}")
        print(f"\nUse when: {opt.best_for}")
        
        rationale = get_score_rationale(opt.name, traffic, control, cost)
        print(f"\nWhy this scored:")
        for reason in rationale:
            print(f"  • {reason}")
        
        print(f"\nPros:")
        for p in opt.pros:
            print(f"  + {p}")
        
        print(f"\nCons:")
        for c in opt.cons:
            print(f"  - {c}")
        
        print(f"\nWatch out for:")
        for c in opt.cons:
            print(f"  ⚠ {c}")
    
    # Explainability timeline for top option
    if ranked:
        top_opt = ranked[0]
        print(f"\n{'='*70}")
        print(f"EXPLAINABILITY TIMELINE (Top Option: {top_opt.name})")
        print(f"{'='*70}")
        print("Step-by-step scoring breakdown:")
        
        factors = ["traffic", "control", "cost"]
        for factor in factors:
            contrib = details["contributions"][top_opt.name][factor]
            reason = details["reasons"][top_opt.name][factor]
            if contrib > 0 or reason:
                print(f"  {factor.capitalize()}: {reason if reason else 'No contribution'}")
                if contrib > 0:
                    print(f"    → Score contribution: +{contrib:.1f}")
            else:
                print(f"  {factor.capitalize()}: No contribution to score")
    
    # What would change this decision
    if ranked:
        suggestions = get_what_would_change(ranked[0].name, traffic, control, cost)
        print(f"\n{'='*70}")
        print("WHAT WOULD CHANGE THIS DECISION?")
        print(f"{'='*70}")
        for suggestion in suggestions:
            print(f"  • {suggestion}")
    
    print("\n" + "="*70)
    print("Note: This is not a single best answer; use the trade-offs above to decide.")
    print("="*70)
    
    # Assumptions
    assumptions = get_assumptions()
    print(f"\n{'='*70}")
    print("ASSUMPTIONS")
    print(f"{'='*70}")
    for assumption in assumptions:
        print(f"  • {assumption}")


if __name__ == "__main__":
    main()