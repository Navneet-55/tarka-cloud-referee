# Tarka – Cloud Compute Referee

Tarka is a small decision-support tool that helps compare AWS compute options by highlighting trade-offs instead of recommending a single “best” choice.

I built this as part of the **AI for Bharat – Kiro Week 6 (“The Referee”) challenge**, which focuses on helping users reason through decisions rather than just consuming answers.

---

## Problem

Choosing the right AWS compute service early in a project can be challenging. Services like **AWS Lambda**, **ECS**, and **EC2** solve different problems, but documentation usually explains them in isolation.

What’s often missing is a clear comparison that explains **why** one option might be more suitable than another under specific constraints.

---

## Approach

Instead of trying to be exhaustive, I focused on a small set of practical factors that commonly influence early architecture decisions:

- Operational overhead  
- Cost sensitivity  
- Traffic patterns  
- Level of infrastructure control  

The tool presents multiple valid options and explains:
- Where each option works well  
- What trade-offs come with that choice  
- When an option should probably be avoided  

The goal is to support informed decision-making, not to replace it.

---

## Implementation

The core logic lives in `referee.py`.

The comparison logic is intentionally kept simple and readable, reflecting how a developer might reason through these choices during early architecture discussions. This is not meant to be a production-ready recommendation engine, but a clear starting point for thinking through trade-offs.

---

## Kiro Usage

I used **Kiro** as a supporting tool during development to:

- Clarify the intent of the challenge  
- Break the problem into decision-focused components  
- Iterate on explanations of trade-offs between services  

All final design and implementation decisions were made manually, with Kiro used only to accelerate iteration and clarify reasoning—not to replace hands-on development.

---

## How to Run

**Requirements:**  
- Python 3.9+

**Run:**
```bash
python referee.py
