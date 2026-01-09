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
# Run all tests
python3 -m unittest discover tests -v

# Run specific test file
python3 -m unittest tests.test_core
python3 -m unittest tests.test_refactoring

# Run with coverage (if coverage.py is installed)
python3 -m coverage run -m unittest discover tests
python3 -m coverage report
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

## Project Structure

- `src/models.py` - Data models (ComputeOption, EvaluationInputs, EvaluationResult, etc.)
- `src/tarka_core.py` - Core evaluation logic and scoring engine
- `src/rendering.py` - Rendering helpers for consistent output formatting
- `src/constants.py` - Constants, type aliases, and scoring rule configuration
- `src/exceptions.py` - Custom exception classes for error handling
- `cli.py` - Command-line interface with type hints and validation
- `ui.py` - Streamlit web interface with theme support
- `tests/test_core.py` - Unit tests for core evaluation logic
- `tests/test_refactoring.py` - Behavior preservation and property-based tests
- `requirements.txt` - Python dependencies
- `.kiro/specs/code-quality-improvements/` - Spec-driven refactoring documentation
  - `requirements.md` - Formal requirements for code quality improvements
  - `design.md` - Comprehensive design document with correctness properties
  - `tasks.md` - Implementation task list with traceability
- `.kiro/notes.md` - Kiro usage notes and development history

## Code Quality

This project follows Python best practices and has undergone comprehensive refactoring:

- **Type Safety**: Full type hints throughout codebase, passes mypy type checking
- **Immutability**: All data models use frozen dataclasses to prevent accidental mutations
- **Error Handling**: Custom exception hierarchy with descriptive error messages
- **Documentation**: Google-style docstrings for all public functions and classes
- **Testing**: 23 tests including property-based tests with 100% behavior preservation
- **Configuration-Driven**: Scoring rules defined as declarative configuration
- **Separation of Concerns**: Clear boundaries between data, logic, and presentation

## Limitations

- **Early-stage focus:** Designed for initial architecture decisions, not production optimization
- **Three options only:** Compares Lambda, ECS/Fargate, and EC2; does not include other AWS services
- **Simplified scoring:** Uses basic rule-based scoring; does not model complex cost calculations or performance benchmarks
- **No compliance modeling:** Does not account for specific compliance requirements (HIPAA, PCI-DSS, etc.)
- **Static assumptions:** Assumes standard AWS regions and typical workload patterns

## Decision Logic Version

**v1.0** - Deterministic, rule-based scoring with explainability

## Kiro Usage

This project was developed with Kiro's assistance for reasoning, iteration, and systematic refactoring. See `.kiro/notes.md` for complete details.

### Initial Development
- Kiro helped clarify the "Referee" challenge intent and iterate on trade-off explanations
- All final design decisions, code structure, and implementation were made manually
- Kiro acted as an accelerator, not a replacement for hands-on development

### Code Quality Improvements (Refactoring Phase)
- Used Kiro's spec-driven development workflow to systematically improve code quality
- Created formal requirements document defining 10 categories of improvements
- Developed comprehensive design document with 6 correctness properties
- Implemented detailed task list with 12 major tasks and property-based tests
- Achieved 100% behavior preservation through comprehensive testing
- All refactoring guided by requirements → design → tasks → implementation workflow

## Notes
Minor documentation update for clarity.
