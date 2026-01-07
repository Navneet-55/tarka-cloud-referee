from src.tarka_core import get_compute_options, score_options, get_score_rationale


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

    options = get_compute_options()
    ranked = score_options(options, traffic, control, cost)

    print("\n" + "="*70)
    print("INPUT SUMMARY")
    print("="*70)
    print(f"Traffic pattern: {traffic}")
    print(f"Infrastructure control: {control}")
    print(f"Cost sensitivity: {cost}")
    print("="*70)

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
    
    print("\n" + "="*70)
    print("Note: This is not a single best answer; use the trade-offs above to decide.")
    print("="*70)


if __name__ == "__main__":
    main()