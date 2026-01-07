# Tarka – Cloud Compute Referee

A lightweight decision-support tool that helps compare AWS compute services (Lambda, ECS/Fargate, EC2) by explaining trade-offs instead of recommending a single "best" option.

## Features

- **Ranked comparison** of AWS Lambda, ECS (Fargate), and EC2 with scores
- **Score rationale** explaining why each option scored based on your inputs
- **Interactive Streamlit UI** with dark mode toggle, card/table views, and visual score indicators
- **Input summary** showing your selected requirements
- **Best fit highlight** for top-ranked option (not a recommendation)
- **Decision snapshot** download (JSON) for saving your analysis
- **Architecture context hints** explaining each service type
- **Watch out for** sections derived from cons
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

- `src/tarka_core.py` - Core comparison logic, scoring, and rationale calculation
- `cli.py` - Command-line interface
- `ui.py` - Streamlit web interface with dark mode, table view, and snapshot export
- `requirements.txt` - Python dependencies
- `.kiro/notes.md` - Kiro usage notes

## Kiro Usage

This project was developed with Kiro's assistance for reasoning and iteration. See `kiro/notes.md` for details.

- Kiro helped clarify the "Referee" challenge intent and iterate on trade-off explanations
- All final design decisions, code structure, and implementation were made manually
- Kiro acted as an accelerator, not a replacement for hands-on development
