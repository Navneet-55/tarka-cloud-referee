# Tarka — Cloud Compute Referee

Explain trade-offs across AWS compute options with transparent, deterministic scoring. Tarka ranks AWS Lambda, ECS (Fargate), and EC2 based on your inputs and clearly explains why — so you can make confident, context-aware decisions rather than chase a single "best" answer.

## Highlights

- **Transparent scoring:** Deterministic, rule-based evaluation across traffic, control, and cost.
- **Clear rationale:** Human-readable reasons behind every score, plus watch-outs.
- **Confidence indicator:** Shows how strong the top pick is vs. alternatives.
- **Two interfaces:** Streamlit UI for interactive use, simple CLI for terminals.
- **Offline-first:** No cloud calls; runs locally with minimal dependencies.

## Quick Start

### Prerequisites
- Python 3.9+ (macOS, Linux, Windows)

### Install
```bash
# Optional: create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
python3 -m pip install -r requirements.txt
```

### Run the UI
```bash
python3 -m streamlit run ui.py
```

### Run the CLI
```bash
python3 cli.py
```

You’ll be prompted for:
- Traffic pattern: `bursty` or `steady`
- Control level: `low`, `medium`, or `high`
- Cost sensitivity: `sensitive` or `flexible`

## Programmatic Use

Use the core scoring directly in Python:

```python
from src.models import EvaluationInputs
from src.tarka_core import evaluate

inputs = EvaluationInputs(
    traffic="bursty",
    control="low",
    cost="sensitive",  # optional: weights={"traffic":1.0, "control":1.0, "cost":1.0}
)

result = evaluate(inputs)
print("Top option:", result.top_option.name)
print("Confidence:", result.confidence_level, "-", result.confidence_message)

for scored in result.ranked_options:
    print(scored.option.name, scored.score)
```

## How It Works

- **Options considered:** AWS Lambda, AWS ECS (Fargate), AWS EC2.
- **Inputs:** `traffic` (`bursty|steady`), `control` (`low|medium|high`), `cost` (`sensitive|flexible`).
- **Scoring rules:** Declarative rules in [src/constants.py](src/constants.py) translate matches into points (with optional weights).
- **Explainability:** Each option includes positive reasons and contextual notes based on your inputs.
- **Confidence:** Computed from the score gap between rank 1 and 2.

## Examples

- **Startup MVP**: `bursty`, `low`, `sensitive` → Typically favors Lambda (pay-per-use, auto-scaling).
- **Enterprise migration**: `steady`, `high`, `flexible` → Typically favors EC2 (full control).
- **Microservices API**: `steady`, `medium`, `flexible` → Typically favors ECS/Fargate (balanced control).

## Project Structure

- [src/models.py](src/models.py) — Data models (`ComputeOption`, `EvaluationInputs`, `EvaluationResult`, …)
- [src/tarka_core.py](src/tarka_core.py) — Core evaluation logic and scoring engine
- [src/rendering.py](src/rendering.py) — Formatting helpers for CLI output
- [src/constants.py](src/constants.py) — Scoring rules, thresholds, and type aliases
- [src/exceptions.py](src/exceptions.py) — Custom exceptions (e.g., `InvalidInputError`)
- [cli.py](cli.py) — Interactive terminal experience
- [ui.py](ui.py) — Streamlit UI with theme and motion system
- [tests/test_core.py](tests/test_core.py) — Unit tests for core logic
- [tests/test_refactoring.py](tests/test_refactoring.py) — Behavior-preservation and property tests
- [requirements.txt](requirements.txt) — Dependencies (Streamlit for UI, Hypothesis for tests)

## Testing

```bash
# Run all tests
python3 -m unittest discover tests -v

# Run specific tests
python3 -m unittest tests.test_core
python3 -m unittest tests.test_refactoring

# Optional coverage (if you install coverage)
python3 -m pip install coverage
python3 -m coverage run -m unittest discover tests
python3 -m coverage report
```

## Limitations

- Focused on early-stage architectural decisions; not a cost/perf optimizer.
- Only compares Lambda, ECS/Fargate, and EC2.
- Simplified rule-based scoring; does not model detailed pricing or benchmarks.
- No compliance modeling (HIPAA, PCI-DSS, etc.).

## Troubleshooting

- Streamlit not found: install with `python3 -m pip install -r requirements.txt`.
- Import errors: ensure you run from the repository root so relative imports resolve.
- Python version: use Python 3.9+; verify with `python3 --version`.

## Notes

Minor documentation refresh for clarity and accuracy.
