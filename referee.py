def compare_compute_options(requirements):
    """
    Compare AWS compute options based on high-level requirements.
    This function intentionally keeps the logic simple and readable.
    """

    options = [
        {
            "name": "AWS Lambda",
            "pros": [
                "No server management",
                "Automatic scaling",
                "Cost-effective for low or bursty traffic"
            ],
            "cons": [
                "Cold start latency",
                "Execution time limits",
                "Less control over runtime environment"
            ],
            "use_when": "Workloads are event-driven and traffic is unpredictable"
        },
        {
            "name": "AWS ECS",
            "pros": [
                "Good balance between control and abstraction",
                "Works well with containerized services",
                "Predictable performance"
            ],
            "cons": [
                "More setup than Lambda",
                "Requires container management"
            ],
            "use_when": "Running microservices with steady or moderate traffic"
        },
        {
            "name": "AWS EC2",
            "pros": [
                "Full control over infrastructure",
                "Flexible instance configurations"
            ],
            "cons": [
                "Highest operational overhead",
                "Manual scaling and maintenance"
            ],
            "use_when": "You need full control or are running legacy workloads"
        }
    ]

    return options


if __name__ == "__main__":
    user_requirements = {
        "cost_sensitive": True,
        "traffic_pattern": "bursty",
        "team_size": "small"
    }

    recommendations = compare_compute_options(user_requirements)

    for option in recommendations:
        print(f"\n{option['name']}")
        print("Pros:", ", ".join(option["pros"]))
        print("Cons:", ", ".join(option["cons"]))
        print("Best used when:", option["use_when"])
