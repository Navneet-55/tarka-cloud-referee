# Tarka – Cloud Compute Referee

A lightweight decision-support tool that helps compare AWS compute services (Lambda, ECS/Fargate, EC2) by explaining trade-offs instead of recommending a single "best" option.

## Features

- **Ranked comparison** of AWS Lambda, ECS (Fargate), and EC2 with scores
- **Score rationale** explaining why each option scored based on your inputs
- **Confidence/Sensitivity indicator** based on score gaps between options
- **What would change this decision** - rule-based suggestions for scenario evolution
- **Assumptions** - explicit assumptions about the decision context
- **Scenario presets** - quick-start buttons (Startup MVP, High-traffic API, Batch processing, Legacy migration)
- **Compare two scenarios** - side-by-side comparison mode
- **Export as Markdown** - download decision analysis as Markdown file
- **Advanced mode** - weighted inputs to emphasize different factors
- **Explainability timeline** - step-by-step scoring breakdown per option
- **Interactive Streamlit UI** with dark mode toggle, card/table views, and visual score indicators
- **CLI interface** for terminal-based usage

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

## Screenshots

Add screenshots to `assets/` directory:
- `assets/ui_home.png` - Home screen with inputs
- `assets/ui_results.png` - Results view with cards/table

## Project Structure

- `src/tarka_core.py` - Core comparison logic, scoring, rationale calculation, and evaluation functions
- `cli.py` - Command-line interface with confidence, explainability, and assumptions
- `ui.py` - Streamlit web interface with presets, compare mode, advanced weights, and exports
- `requirements.txt` - Python dependencies
- `kiro/notes.md` - Kiro usage notes

## Kiro Usage

This project was developed with Kiro's assistance for reasoning and iteration. See `kiro/notes.md` for details.

- Kiro helped clarify the "Referee" challenge intent and iterate on trade-off explanations
- All final design decisions, code structure, and implementation were made manually
- Kiro acted as an accelerator, not a replacement for hands-on development
