# Tarka – Cloud Compute Referee

Tarka is a lightweight decision-support tool that helps compare AWS compute services by explaining **trade-offs** instead of recommending a single “best” option.

It is designed to reflect how engineers reason about infrastructure choices early in a project, when requirements are still evolving.

This project was built as part of the **AI for Bharat – Kiro Week 6 (“The Referee”) challenge**.

---

## Problem

Choosing the right AWS compute service early in a project can be confusing.

Services like **AWS Lambda**, **ECS (Fargate)**, and **EC2** all solve different problems, but documentation usually explains them in isolation. What’s often missing is a clear explanation of **why** one option might be preferable over another under specific constraints.

---

## Approach

Instead of trying to be exhaustive, Tarka focuses on a small set of practical decision factors:

- Traffic patterns (bursty vs steady)
- Level of infrastructure control required
- Cost sensitivity

The tool compares multiple valid options and explains:
- Where each option works well
- The trade-offs involved
- When an option may *not* be ideal

The goal is to support **informed decision-making**, not to replace it.

---

## Implementation

- Core comparison logic lives in `src/tarka_core.py`
- `cli.py` provides a command-line interface
- `ui.py` provides a simple Streamlit-based UI
- Logic is intentionally explicit and readable, mirroring how these decisions are discussed during early architecture planning

This is **not** a production recommendation engine. It is a clear, opinionated starting point for reasoning about AWS compute trade-offs.

---

## How to Run

### Requirements

- Python 3.9+

### Install dependencies

```bash
pip install -r requirements.txt