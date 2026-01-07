from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


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


def score_options(options, traffic, control, cost, weights=None):
    """Score options with optional weights. Returns ranked list."""
    if weights is None:
        weights = {"traffic": 1.0, "control": 1.0, "cost": 1.0}
    
    # Normalize weights
    total = sum(weights.values())
    if total > 0:
        weights = {k: v / total * len(weights) for k, v in weights.items()}
    
    for opt in options:
        if traffic == "bursty" and opt.name == "AWS Lambda":
            opt.score += 2 * weights.get("traffic", 1.0)
        if traffic == "steady" and opt.name == "AWS ECS (Fargate)":
            opt.score += 2 * weights.get("traffic", 1.0)
        if control == "high" and opt.name == "AWS EC2":
            opt.score += 2 * weights.get("control", 1.0)
        if cost == "sensitive" and opt.name == "AWS Lambda":
            opt.score += 1 * weights.get("cost", 1.0)
        if control == "medium" and opt.name == "AWS ECS (Fargate)":
            opt.score += 1 * weights.get("control", 1.0)

    return sorted(options, key=lambda x: x.score, reverse=True)


def evaluate(traffic, control, cost, weights=None):
    """
    Evaluate inputs and return structured results with contributions and reasons.
    Returns: (ranked_options, details_dict)
    """
    options = get_compute_options()
    ranked = score_options(options, traffic, control, cost, weights)
    
    # Calculate contributions per factor
    contributions = {}
    reasons = {}
    
    for opt in options:
        contributions[opt.name] = {"traffic": 0.0, "control": 0.0, "cost": 0.0}
        reasons[opt.name] = {"traffic": "", "control": "", "cost": ""}
        
        w_traffic = weights.get("traffic", 1.0) if weights else 1.0
        w_control = weights.get("control", 1.0) if weights else 1.0
        w_cost = weights.get("cost", 1.0) if weights else 1.0
        
        if opt.name == "AWS Lambda":
            if traffic == "bursty":
                contributions[opt.name]["traffic"] = 2.0 * w_traffic
                reasons[opt.name]["traffic"] = "Bursty traffic pattern (+2)"
            if cost == "sensitive":
                contributions[opt.name]["cost"] = 1.0 * w_cost
                reasons[opt.name]["cost"] = "Cost-sensitive workload (+1)"
        
        elif opt.name == "AWS ECS (Fargate)":
            if traffic == "steady":
                contributions[opt.name]["traffic"] = 2.0 * w_traffic
                reasons[opt.name]["traffic"] = "Steady traffic pattern (+2)"
            if control == "medium":
                contributions[opt.name]["control"] = 1.0 * w_control
                reasons[opt.name]["control"] = "Medium control requirement (+1)"
        
        elif opt.name == "AWS EC2":
            if control == "high":
                contributions[opt.name]["control"] = 2.0 * w_control
                reasons[opt.name]["control"] = "High control requirement (+2)"
    
    details = {
        "contributions": contributions,
        "reasons": reasons,
        "normalized_inputs": {"traffic": traffic, "control": control, "cost": cost}
    }
    
    return ranked, details


def get_confidence(ranked):
    """Calculate confidence based on score gap between rank 1 and 2."""
    if len(ranked) < 2:
        return "High", "Score gap calculation requires at least 2 options"
    
    gap = ranked[0].score - ranked[1].score
    if gap >= 3:
        return "High", f"Score gap of {gap:.1f} indicates clear preference"
    elif gap == 2:
        return "Medium", f"Score gap of {gap:.1f} suggests moderate confidence"
    else:
        return "Low", f"Score gap of {gap:.1f} indicates close competition"


def get_what_would_change(top_option, traffic, control, cost):
    """Generate rule-based suggestions for what would change the decision."""
    suggestions = []
    
    if top_option == "AWS Lambda":
        if traffic == "bursty":
            suggestions.append("If workload becomes steady/always-on, ECS/Fargate or EC2 may become better fit")
        if control == "low":
            suggestions.append("If control needs increase, consider ECS/Fargate or EC2")
        if cost == "sensitive":
            suggestions.append("If cost becomes less critical, ECS/Fargate may offer better runtime control")
        suggestions.append("If execution time exceeds Lambda limits, move to ECS/Fargate or EC2")
        suggestions.append("If you need custom networking or storage, EC2 may be required")
    
    elif top_option == "AWS ECS (Fargate)":
        if traffic == "steady":
            suggestions.append("If traffic becomes highly bursty, Lambda may be more cost-effective")
        if control == "medium":
            suggestions.append("If control needs decrease, Lambda may simplify operations")
            suggestions.append("If control needs increase significantly, EC2 may be required")
        suggestions.append("If container management overhead becomes too high, consider Lambda or EC2")
    
    elif top_option == "AWS EC2":
        if control == "high":
            suggestions.append("If ops appetite decreases, ECS/Fargate or Lambda may reduce overhead")
        if traffic == "steady":
            suggestions.append("If traffic becomes bursty, Lambda may be more cost-effective")
        suggestions.append("If you don't need full infrastructure control, ECS/Fargate or Lambda may be simpler")
        suggestions.append("If cost becomes critical, Lambda's pay-per-use model may be better")
    
    return suggestions if suggestions else ["Consider reviewing all trade-offs as requirements evolve"]


def get_assumptions():
    """Return list of assumptions for the tool."""
    return [
        "No special hardware requirements (GPU, custom chips, etc.)",
        "Early-stage architecture decision (requirements may evolve)",
        "No strict compliance constraints modeled (HIPAA, PCI-DSS, etc.)",
        "Standard AWS regions and availability zones",
        "Workload can be containerized or run as functions (if applicable)"
    ]