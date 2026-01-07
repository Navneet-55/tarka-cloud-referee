from dataclasses import dataclass
from typing import List


@dataclass
class ComputeOption:
    name: str
    pros: List[str]
    cons: List[str]
    best_for: str
    score: int = 0


def get_compute_options() -> List[ComputeOption]:
    return [
        ComputeOption(
            name="AWS Lambda",
            pros=[
                "No server management",
                "Automatic scaling",
                "Pay per execution"
            ],
            cons=[
                "Cold start latency",
                "Execution time limits",
                "Limited runtime control"
            ],
            best_for="Event-driven or bursty workloads"
        ),
        ComputeOption(
            name="AWS ECS (Fargate)",
            pros=[
                "Good balance of control and abstraction",
                "Works well with containers",
                "Predictable runtime"
            ],
            cons=[
                "More setup than Lambda",
                "Container image management required"
            ],
            best_for="Microservices with steady traffic"
        ),
        ComputeOption(
            name="AWS EC2",
            pros=[
                "Maximum infrastructure control",
                "Custom networking and storage",
                "Suitable for legacy workloads"
            ],
            cons=[
                "Highest operational overhead",
                "Manual scaling unless automated",
                "Requires patching and monitoring"
            ],
            best_for="Workloads requiring full control"
        ),
    ]


def score_options(options, traffic, control, cost):
    for opt in options:
        if traffic == "bursty" and opt.name == "AWS Lambda":
            opt.score += 2
        if traffic == "steady" and opt.name == "AWS ECS (Fargate)":
            opt.score += 2
        if control == "high" and opt.name == "AWS EC2":
            opt.score += 2
        if cost == "sensitive" and opt.name == "AWS Lambda":
            opt.score += 1
        if control == "medium" and opt.name == "AWS ECS (Fargate)":
            opt.score += 1

    return sorted(options, key=lambda x: x.score, reverse=True)