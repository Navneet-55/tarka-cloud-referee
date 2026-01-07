# Tarka — Cloud Compute Referee

A constraint-aware decision-support tool that helps developers reason through AWS compute choices by explaining trade-offs rather than recommending a single "best" option.

## Quick Demo (30 seconds)

1. **Run the UI:**
   ```bash
   streamlit run ui.py
   ```

2. **Select inputs:**
   - Traffic: Bursty / unpredictable
   - Control: Low
   - Cost: Very sensitive
   - Click "Compare Options"

3. **Review results:**
   - See ranked options (Lambda, ECS/Fargate, EC2)
   - Check confidence indicator
   - Expand "Why this scored" for each option
   - Review pros, cons, and watch-outs

## Features

- **Ranked comparison** of AWS Lambda, ECS (Fargate), and EC2 with scores
- **Deterministic scoring** based on traffic patterns, infrastructure control, and cost sensitivity
- **Confidence indicator** derived from score gaps between options
- **Explainability** showing why each option scored based on inputs
- **Interactive Streamlit UI** with light/dark themes and smooth animations
- **CLI interface** for terminal-based usage
- **Export capabilities** (Markdown, copyable summary)
- **Offline-first** with no external APIs or cloud calls

## How to Run

### Prerequisites
- Python 3.9+

### Installation
```bash
# Optional: create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
python3 -m pip install -r requirements.txt
```

### CLI
```bash
python3 cli.py
```

### Streamlit UI
```bash
python3 -m streamlit run ui.py
```

### Run Tests
```bash
python3 -m unittest tests.test_core
```

## Example Scenarios

### Scenario 1: Startup MVP
**Inputs:**
- Traffic: Bursty / unpredictable
- Control: Low
- Cost: Very sensitive

**Expected Top Ranking:** AWS Lambda
**Reasoning:** Bursty traffic and cost sensitivity favor Lambda's pay-per-use model and auto-scaling.

### Scenario 2: Enterprise Migration
**Inputs:**
- Traffic: Steady / predictable
- Control: High
- Cost: Flexible

**Expected Top Ranking:** AWS EC2
**Reasoning:** High control needs and steady traffic favor EC2's full infrastructure control.

### Scenario 3: Microservices API
**Inputs:**
- Traffic: Steady / predictable
- Control: Medium
- Cost: Flexible

**Expected Top Ranking:** AWS ECS (Fargate)
**Reasoning:** Steady traffic and medium control needs align with ECS/Fargate's balanced approach.

## Screenshots

![Home Screen](assets/ui_home.png)
*Home screen with input controls and presets*

![Results View](assets/ui_results.png)
*Results view showing ranked options with scores and trade-offs*

## Project Structure

- `src/models.py` - Data models (ComputeOption, EvaluationInputs, EvaluationResult)
- `src/tarka_core.py` - Core evaluation logic and scoring
- `src/rendering.py` - Rendering helpers for consistent output
- `cli.py` - Command-line interface
- `ui.py` - Streamlit web interface
- `tests/test_core.py` - Unit tests for core logic
- `requirements.txt` - Python dependencies
- `.kiro/notes.md` - Kiro usage notes

## Limitations

- **Early-stage focus:** Designed for initial architecture decisions, not production optimization
- **Three options only:** Compares Lambda, ECS/Fargate, and EC2; does not include other AWS services
- **Simplified scoring:** Uses basic rule-based scoring; does not model complex cost calculations or performance benchmarks
- **No compliance modeling:** Does not account for specific compliance requirements (HIPAA, PCI-DSS, etc.)
- **Static assumptions:** Assumes standard AWS regions and typical workload patterns

## Decision Logic Version

**v1.0** - Deterministic, rule-based scoring with explainability

## Kiro Usage

This project was developed with Kiro's assistance for reasoning and iteration. See `.kiro/notes.md` for details.

- Kiro helped clarify the "Referee" challenge intent and iterate on trade-off explanations
- All final design decisions, code structure, and implementation were made manually
- Kiro acted as an accelerator, not a replacement for hands-on development
