# ⚖️ Tarka — Cloud Compute Referee

<div align="center">

**Transparent. Deterministic. Explainable.**

Confidently navigate AWS compute choices with intelligent trade-off analysis.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![Tests: 23/23 Passing](https://img.shields.io/badge/tests-23%2F23%20passing-brightgreen?style=flat-square)](tests/)
[![MIT License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Type Safe](https://img.shields.io/badge/type%20safety-100%25-blue?style=flat-square)](#-code-quality)
[![Offline-First](https://img.shields.io/badge/offline--first-enabled-brightgreen?style=flat-square)](#-how-it-works)

[🚀 Get Started](#-quick-start) • [📖 Docs](#-how-it-works) • [💻 Examples](#️-example-scenarios) • [🧪 Tests](#-testing)

</div>

---

## 🎯 What is Tarka?

Explain trade-offs across AWS compute options with **transparent, deterministic scoring**. Tarka ranks **AWS Lambda, ECS (Fargate), and EC2** based on your inputs and clearly explains **why** — so you can make confident, context-aware decisions rather than chase a single "best" answer.

Perfect for **architects, DevOps engineers, and startup founders** making early-stage infrastructure decisions.

## ✨ Key Features

| Feature | Details |
|---------|---------|
| 🔍 **Transparent Scoring** | Deterministic, rule-based evaluation across traffic, control, and cost |
| 📊 **Clear Rationale** | Human-readable explanations for every score, plus watch-outs |
| 📈 **Confidence Metrics** | Understand recommendation strength vs. alternatives |
| 🎨 **Dual Interfaces** | Interactive Streamlit UI + lightweight CLI |
| 🚀 **Offline-First** | Zero cloud calls, instant results, privacy by default |
| 🔧 **Type-Safe** | Full type hints, frozen dataclasses, 23/23 tests passing |

---

## 🛠️ Tech Stack

Built with modern Python tools for clarity and maintainability:

| Component | Technology | Link |
|-----------|-----------|------|
| **Language** | [Python 3.9+](https://www.python.org/) | High-level, readable |
| **Web UI** | [Streamlit 1.28+](https://streamlit.io/) | Rapid, interactive dashboards |
| **Testing** | [Hypothesis 6.0+](https://hypothesis.readthedocs.io/) | Property-based testing |
| **Data Models** | [Dataclasses](https://docs.python.org/3/library/dataclasses.html) | Immutable, type-safe |
| **Scoring Engine** | Custom rule-based system | 100% deterministic |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** ([download](https://www.python.org/downloads/))
- macOS, Linux, or Windows

### 1️⃣ Install

```bash
# Clone or download the repository
cd tarka-cloud-referee

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
python3 -m pip install -r requirements.txt
```

### 2️⃣ Run the Interactive UI

```bash
python3 -m streamlit run ui.py
```

Opens at `http://localhost:8501` with:
- ✅ Light/dark theme toggle
- ✅ Smooth animations
- ✅ Real-time scoring
- ✅ Confidence indicators

### 3️⃣ Run the CLI

```bash
python3 cli.py
```

Interactive terminal prompts for:
- **Traffic pattern:** `bursty` (unpredictable spikes) or `steady` (consistent load)
- **Control level:** `low` (managed services) | `medium` (balanced) | `high` (full control)
- **Cost sensitivity:** `sensitive` (cost-focused) or `flexible` (less constrained)

---

## 💻 Programmatic Usage

Integrate Tarka scoring into your own tools:

```python
from src.models import EvaluationInputs
from src.tarka_core import evaluate

# Define your requirements
inputs = EvaluationInputs(
    traffic="bursty",           # or "steady"
    control="low",              # or "medium", "high"
    cost="sensitive",           # or "flexible"
    weights={                   # Optional: adjust factor importance
        "traffic": 1.0,
        "control": 1.0,
        "cost": 1.0
    }
)

# Get deterministic results
result = evaluate(inputs)

# Access results
print(f"🏆 Top option: {result.top_option.name}")
print(f"📊 Confidence: {result.confidence_level}")
print(f"💬 Why: {result.confidence_message}")
print()

# See all ranked options with scores
for scored in result.ranked_options:
    option = scored.option
    print(f"\n{option.name} (Score: {scored.score})")
    print(f"  Best for: {option.best_for}")
    print(f"  Pros: {', '.join(option.pros)}")
    print(f"  Cons: {', '.join(option.cons)}")
```

**Output:**
```
🏆 Top option: AWS Lambda
📊 Confidence: High
💬 Why: Score gap of 3.0 indicates clear preference

AWS Lambda (Score: 3.0)
  Best for: Event-driven or bursty workloads
  Pros: No server management, Automatic scaling, Pay per execution
  Cons: Cold start latency, Execution time limits, Limited runtime control
```

---

## 📖 How It Works

### Scoring Model

| Compute Option | Factors | Scoring Rules |
|---|---|---|
| **AWS Lambda** | ✅ Bursty traffic (+2) <br> ✅ Cost sensitivity (+1) | Ideal for unpredictable loads with pay-per-use needs |
| **AWS ECS (Fargate)** | ✅ Steady traffic (+2) <br> ✅ Medium control (+1) | Balanced containerized workloads |
| **AWS EC2** | ✅ High control needs (+2) | Maximum flexibility & infrastructure control |

### Confidence Calculation

- **High:** Score gap ≥ 3.0 (clear winner)
- **Medium:** Score gap 2.0–2.9 (moderate preference)
- **Low:** Score gap < 2.0 (close race, review trade-offs)

### Explainability Pipeline

```
Inputs (traffic, control, cost)
    ↓
Match scoring rules → Calculate contributions
    ↓
Weight contributions (user-configurable)
    ↓
Rank options by total score
    ↓
Generate rationale + watch-outs
    ↓
Calculate confidence from score gap
    ↓
Output: Ranked options with explanations
```

---

## 🎯 Example Scenarios

### Scenario 1: Startup MVP ⚡
```
Inputs: bursty traffic, low control, cost-sensitive
Expected winner: AWS Lambda

Why? 
  • Bursty traffic → Lambda auto-scales (+2)
  • Cost-sensitive → pay-per-use model (+1)
  • Low control → managed service fits
  → Total: 3.0 (High confidence)
```

### Scenario 2: Enterprise Workload 🏢
```
Inputs: steady traffic, high control, flexible budget
Expected winner: AWS EC2

Why?
  • High control → full infrastructure access (+2)
  • Steady traffic → no need for auto-scaling
  • Flexible budget → can absorb operational costs
  → EC2 and ECS tie; EC2 chosen for maximum control
```

### Scenario 3: Microservices Platform 🐳
```
Inputs: steady traffic, medium control, flexible budget
Expected winner: AWS ECS (Fargate)

Why?
  • Steady traffic → ECS thrives (+2)
  • Medium control → Fargate balances abstraction + control (+1)
  • Containers → natural fit for microservices
  → Total: 3.0 (High confidence)
```

---

## 📁 Project Structure

```
tarka-cloud-referee/
├── src/
│   ├── models.py              # Data models (ComputeOption, EvaluationInputs, etc.)
│   ├── tarka_core.py          # Core evaluation engine & scoring logic
│   ├── rendering.py           # Formatting helpers for CLI output
│   ├── constants.py           # Scoring rules, thresholds, type aliases
│   ├── exceptions.py          # Custom exceptions (InvalidInputError)
│   └── __init__.py
├── tests/
│   ├── test_core.py           # Unit tests for core logic
│   ├── test_refactoring.py    # Property-based & behavior tests
│   └── __init__.py
├── cli.py                     # Terminal-based interface
├── ui.py                      # Streamlit web interface
├── requirements.txt           # Dependencies: streamlit, hypothesis
├── README.md                  # This file
└── CHANGELOG.md               # Version history
```

---

## 🧪 Testing

All 23 tests pass with 100% behavior preservation:

```bash
# Run all tests
python3 -m unittest discover tests -v

# Run specific test suites
python3 -m unittest tests.test_core          # Core evaluation tests
python3 -m unittest tests.test_refactoring   # Behavior preservation + property tests

# View test coverage (requires coverage.py)
python3 -m pip install coverage
python3 -m coverage run -m unittest discover tests
python3 -m coverage report
```

### Test Categories

- **Unit Tests** (4 tests): Core evaluation logic
- **Behavior Preservation** (16 tests): All input combinations
- **Property-Based Tests** (3 tests): Hypothesis-powered generative testing
  - ✅ Refactoring preserves behavior
  - ✅ Score determinism
  - ✅ Input immutability

---

## 📊 Code Quality

| Metric | Status |
|--------|--------|
| **Type Safety** | ✅ 100% type-hinted, passes mypy |
| **Immutability** | ✅ All models frozen (dataclasses) |
| **Tests** | ✅ 23/23 passing |
| **Documentation** | ✅ Google-style docstrings |
| **Error Handling** | ✅ Custom exceptions, validation |
| **Determinism** | ✅ No randomness, no external calls |

---

## 🎨 Features in Detail

### Streamlit UI
- 🌓 Light & dark theme support
- ✨ Smooth fade-in animations
- 📱 Mobile-responsive design
- 🎛️ Interactive input sliders & selectors
- 📋 Expandable result cards with watch-outs
- 💾 Session state preservation

### CLI
- 🖥️ Colorful terminal output
- 🎯 Input validation & feedback
- 📊 Explainability timeline
- 💡 "What would change?" suggestions
- 🔄 Repeatable workflow

---

## ⚠️ Limitations

- **Early-stage focus:** Designed for initial architecture decisions, not production optimization
- **Three options only:** Compares Lambda, ECS/Fargate, EC2; excludes other AWS services (AppRunner, etc.)
- **Simplified scoring:** Rule-based model; does not include detailed cost calculations or performance benchmarks
- **No compliance modeling:** Does not account for regulatory requirements (HIPAA, PCI-DSS, etc.)
- **Static assumptions:** Assumes standard AWS regions and typical workload patterns

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'streamlit'` | Run `python3 -m pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'src'` | Ensure you're running from repository root |
| `Python version too old` | Install Python 3.9+ from [python.org](https://www.python.org/downloads/) |
| Streamlit port already in use | Run `streamlit run ui.py --server.port 8502` |
| Import errors in IDE | Verify your IDE uses the correct Python interpreter (`.venv/bin/python`) |

---

## 🤝 Contributing

We welcome issues, ideas, and pull requests! Areas for enhancement:

- [ ] Add more AWS compute options (AppRunner, Batch, etc.)
- [ ] Advanced cost modeling integration
- [ ] Historical tracking of decisions
- [ ] Export to PDF/JSON reports
- [ ] Compliance rule builder

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 📞 Support

- 📖 Check [Project Structure](#-project-structure) and [How It Works](#-how-it-works)
- 🔍 Search [existing issues](../../issues)
- 💬 Open a new issue with details

---

<div align="center">

**Built with ❤️ for cloud architects, DevOps engineers, and startup founders**

[⬆ Back to Top](#️-tarka--cloud-compute-referee)

</div>
