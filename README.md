# Tarka – Cloud Compute Referee

A lightweight decision-support tool that helps compare AWS compute services (Lambda, ECS/Fargate, EC2) by explaining trade-offs instead of recommending a single "best" option.

## How to Run

### CLI
```bash
python cli.py
```

### Streamlit UI
```bash
streamlit run ui.py
```

## Project Structure

- `src/tarka_core.py` - Core comparison logic and scoring
- `cli.py` - Command-line interface
- `ui.py` - Streamlit web interface
- `requirements.txt` - Python dependencies

## Kiro Usage

- Kiro helped with reasoning and iteration during development
- Used to interpret the "Referee" challenge and break down decision components
- All final design decisions and implementation were made manually
