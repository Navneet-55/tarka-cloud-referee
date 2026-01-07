from src.tarka_core import get_compute_options, score_options


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

    print("\nRecommended options (ranked):")
    for opt in ranked:
        print(f"\n{opt.name}")
        print(f"Best for: {opt.best_for}")
        print("Pros:")
        for p in opt.pros:
            print(f"  - {p}")
        print("Cons:")
        for c in opt.cons:
            print(f"  - {c}")


if __name__ == "__main__":
    main()