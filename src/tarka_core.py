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


def get_score_rationale(option_name, traffic, control, cost):
    """Generate deterministic score rationale based on inputs."""
    reasons = []
    
    if option_name == "AWS Lambda":
        if traffic == "bursty":
            reasons.append("Bursty traffic pattern (+2)")
        if cost == "sensitive":
            reasons.append("Cost-sensitive workload (+1)")
        if control == "high":
            reasons.append("High control needs may limit fit")
        if traffic == "steady":
            reasons.append("Steady traffic may not need Lambda's auto-scaling")
    
    elif option_name == "AWS ECS (Fargate)":
        if traffic == "steady":
            reasons.append("Steady traffic pattern (+2)")
        if control == "medium":
            reasons.append("Medium control requirement (+1)")
        if traffic == "bursty":
            reasons.append("Bursty traffic may prefer serverless")
        if control == "high":
            reasons.append("High control needs may require EC2")
    
    elif option_name == "AWS EC2":
        if control == "high":
            reasons.append("High control requirement (+2)")
        if traffic == "bursty":
            reasons.append("Bursty traffic may prefer serverless")
        if cost == "sensitive":
            reasons.append("Cost-sensitive workloads may prefer pay-per-use")
        if control == "low":
            reasons.append("Low control needs may prefer managed services")
    
    return reasons if reasons else ["Base score (no specific matches)"]


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