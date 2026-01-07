# Tarka — Cloud Compute Referee

A constraint-aware decision-support tool that helps developers reason through AWS compute choices by explaining trade-offs rather than recommending a single "best" option.

## Features

- **Ranked comparison** of AWS Lambda, ECS (Fargate), and EC2 with scores
- **Deterministic scoring** based on traffic patterns, infrastructure control, and cost sensitivity
- **Confidence indicator** derived from score gaps between options
- **Explainability** showing why each option scored based on inputs
- **Interactive Streamlit UI** with light/dark themes and smooth animations
- **CLI interface** for terminal-based usage
- **Export capabilities** (Markdown, JSON, copyable summary)
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
pip install -r requirements.txt
```

### CLI
```bash
python cli.py
```

### Streamlit UI
```bash
streamlit run ui.py
```

## Project Structure

- `src/models.py` - Data models (ComputeOption, EvaluationInputs, EvaluationResult)
- `src/tarka_core.py` - Core evaluation logic and scoring
- `src/rendering.py` - Rendering helpers for consistent output
- `cli.py` - Command-line interface
- `ui.py` - Streamlit web interface
- `requirements.txt` - Python dependencies
- `.kiro/notes.md` - Kiro usage notes

## Screenshots

Add screenshots to `assets/` directory:
- `assets/ui_home.png` - Home screen with inputs
- `assets/ui_results.png` - Results view with ranked options

## Kiro Usage

This project was developed with Kiro's assistance for reasoning and iteration. See `.kiro/notes.md` for details.

- Kiro helped clarify the "Referee" challenge intent and iterate on trade-off explanations
- All final design decisions, code structure, and implementation were made manually
- Kiro acted as an accelerator, not a replacement for hands-on development
