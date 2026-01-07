#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Option:
    name: str
    pros: List[str]
    cons: List[str]
    use_when: str
    score: int = 0


def build_options() -> List[Option]:
    return [
        Option(
            name="AWS Lambda",
            pros=["No server management", "Automatic scaling", "Cost-effective for bursty traffic"],
            cons=["Cold start latency", "Execution time limits", "Less runtime control"],
            use_when="Event-driven workloads with unpredictable traffic",
        ),
        Option(
            name="AWS ECS (Fargate)",
            pros=["Good control/abstraction balance", "Works well for containerized services", "Predictable runtime"],
            cons=["More setup than Lambda", "Container/image management required"],
            use_when="Microservices with steady/moderate traffic",
        ),
        Option(
            name="AWS EC2",
            pros=["Maximum control", "Flexible networking and storage options", "Good for custom stacks"],
            cons=["Highest ops overhead", "Manual scaling unless configured", "Requires patching/monitoring"],
            use_when="Legacy workloads, special requirements, or full infra control needed",
        ),
    ]


def ask(prompt: str, choices: Dict[str, str]) -> str:
    print(f"\n{prompt}")
    for k, v in choices.items():
        print(f"  {k}) {v}")
    while True:
        val = input("Choose: ").strip().lower()
        if val in choices:
            return val
        print("Invalid input. Try again.")


def score_options(options: List[Option], traffic: str, ops: str, control: str) -> None:
    for opt in options:
        opt.score = 0

        # traffic
        if traffic == "b":  # bursty
            if opt.name == "AWS Lambda":
                opt.score += 3
            if "ECS" in opt.name:
                opt.score += 1
        if traffic == "s":  # steady
            if "ECS" in opt.name:
                opt.score += 3
            if opt.name == "AWS EC2":
                opt.score += 2

        # ops tolerance
        if ops == "l":  # low ops
            if opt.name == "AWS Lambda":
                opt.score += 3
            if "ECS" in opt.name:
                opt.score += 2
            if opt.name == "AWS EC2":
                opt.score += 0
        if ops == "h":  # high ops ok
            if opt.name == "AWS EC2":
                opt.score += 2

        # control required
        if control == "h":
            if opt.name == "AWS EC2":
                opt.score += 3
            if "ECS" in opt.name:
                opt.score += 2
        if control == "l":
            if opt.name == "AWS Lambda":
                opt.score += 2


def print_results(options: List[Option]) -> None:
    options_sorted = sorted(options, key=lambda o: o.score, reverse=True)
    print("\n=== Tarka Recommendation View (Trade-off Comparison) ===\n")
    for opt in options_sorted:
        print(f"{opt.name}  (score: {opt.score})")
        print(f"Use when: {opt.use_when}")
        print("Pros:")
        for p in opt.pros:
            print(f"  - {p}")
        print("Cons:")
        for c in opt.cons:
            print(f"  - {c}")
        print("-" * 60)

    top = options_sorted[0]
    print(f"\nMost aligned option based on your inputs: {top.name}")
    print("Note: This is not a single 'best' answer—use the trade-offs above to decide.\n")


def main() -> None:
    print("Tarka — Cloud Compute Referee")
    print("Answer a few questions to compare AWS compute options.\n")

    traffic = ask(
        "What best describes your traffic pattern?",
        {"b": "Bursty / unpredictable", "s": "Steady / predictable"},
    )
    ops = ask(
        "How much operational overhead can you take on?",
        {"l": "Low (prefer minimal infra management)", "h": "High (we can manage servers/ops)"},
    )
    control = ask(
        "How much control do you need over runtime/infrastructure?",
        {"l": "Low (managed is fine)", "h": "High (need OS/runtime control)"},
    )

    options = build_options()
    score_options(options, traffic=traffic, ops=ops, control=control)
    print_results(options)


if __name__ == "__main__":
    main()
