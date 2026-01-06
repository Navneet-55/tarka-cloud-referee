# Tarka – Cloud Compute Referee

Tarka is a small decision-support tool that helps compare AWS compute options by highlighting trade-offs instead of recommending a single “best” choice.

I built this as part of the AI for Bharat – Kiro Week 6 challenge, which focuses on helping users reason through decisions rather than just consuming answers.

## Problem

Choosing the right AWS compute service is often confusing, especially early in a project. Services like Lambda, ECS, and EC2 all solve different problems, but documentation usually describes them in isolation.

What’s often missing is a clear comparison that explains *why* one option might be better than another under specific constraints.

## Approach

Instead of trying to be exhaustive, I focused on a small set of practical factors:
- Operational overhead
- Cost sensitivity
- Traffic patterns
- Level of infrastructure control

The tool presents multiple valid options and explains:
- Where each option works well
- What trade-offs come with that choice
- When an option should probably be avoided

The goal is to support informed decision-making, not to replace it.

## Implementation

The core logic lives in `referee.py`.  
It keeps the comparison logic intentionally simple and readable, reflecting how a developer might reason through these choices during early architecture discussions.

This is not meant to be a production-ready recommendation engine, but a clear starting point for thinking through trade-offs.

## Kiro Usage

I used Kiro as a supporting tool during development to:
- Clarify the intent of the challenge
- Break the problem into decision-focused components
- Iterate on explanations of trade-offs

All final design decisions and structure were driven by my own judgment, with Kiro helping speed up iteration rather than replacing manual development.
