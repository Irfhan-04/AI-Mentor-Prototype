# Assessment Brief — AI/ML Internship Assessment

Original brief as received, reproduced here for reference alongside the
implementation and the Architecture Decision Report.

## Your Mission

You have recently joined the AI Engineering team. Your first
responsibility is to help determine the best way to build the AI Mentor
feature.

Three possible implementation strategies were identified:

- Fine-tuning a Large Language Model
- Retrieval-Augmented Generation (RAG)
- Prompt Engineering using an existing Large Language Model API

Task: evaluate these approaches and recommend one that best fits the
company's current constraints, backed by a working proof of concept.

## Problem Statement

Design and develop a minimal prototype that accepts a ~200-word startup
idea submitted by a student and generates structured feedback containing:

- Startup Viability Score
- Key Risks
- Strengths
- Two actionable recommendations for improvement

Business constraints to weigh in the recommendation:

- Limited engineering resources
- Near-zero infrastructure budget
- Small development team with limited ML expertise
- MVP expected within two weeks
- Solution must be maintainable as the platform grows

## Deliverables

1. **Working Prototype** — a runnable application or notebook demonstrating
   the chosen approach against at least three different startup ideas.
2. **Architecture Decision Report** — comparing fine-tuning, RAG, and
   prompt engineering, and justifying the selected approach.
3. **Failure Analysis** — one realistic scenario where the prototype
   produces poor or misleading feedback: why it failed, the business
   impact, and how it would be improved in future iterations.

## Technical Constraints

- Use only free-tier APIs or open-source models
- Paid fine-tuning services are not permitted
- Output must be returned in a structured format (JSON or equivalent)
- All implementation decisions should be documented

## Submission Format

- GitHub Repository
- Architecture Decision Report (PDF)
- README
- AI Usage Declaration

## Where each deliverable lives in this repo

| Brief requirement | Location |
|---|---|
| Working prototype | `src/`, run via `src/cli.py` or `notebooks/demo.ipynb` |
| ≥3 startup ideas | `samples/idea_strong.txt`, `idea_mediocre.txt`, `idea_weak.txt` (plus `idea_adversarial.txt` for the failure analysis) |
| Architecture Decision Report | `ARCHITECTURE_DECISION_REPORT.md` / `.pdf` |
| Failure Analysis | `ARCHITECTURE_DECISION_REPORT.md`, Section 6 |
| README | `README.md` |
| AI Usage Declaration | `AI_USAGE_DECLARATION.md` |
