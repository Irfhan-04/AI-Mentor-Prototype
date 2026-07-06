# Aurstrat Technology — AI/ML Internship Assessment (Original Brief)

> Verbatim from the assessment email + linked assessment document. Kept here so
> every chat in this project has the full spec without re-pasting it.

## Email

Dear Candidate,

Thank you for applying for the AI/ML Internship at Aurstrat Technology. We are
pleased to invite you to the next stage of our recruitment process.

- Assessment Portal: https://app.notion.com/p/AI-ML-Internship-Assessment-38f2dad54ade808d808de7d1c1a7f25e
- Submission Form: https://docs.google.com/forms/d/e/1FAIpQLSfX2ifFh4w1BTH0If1pnxhv2NRsItSrc83F6h1aF2MwVe7O1w/viewform
- Submission Deadline: Within 5 days of receiving this email.

Please read all instructions carefully before starting the assessment. We
encourage original thinking, clear documentation, and practical
problem-solving. Shortlisted candidates will be invited for a technical
interview.

Best regards, Team Aurstrat Technology

## AI/ML Internship Assessment

Welcome to the AI/ML Internship Assessment at Aurstrat Technology.

Artificial Intelligence is transforming how products are built — but in
startups, success isn't measured by model complexity. It's measured by
whether your solution solves a real customer problem within the available
time, budget, and engineering resources.

This assessment simulates a real product challenge that our engineering team
could face. Your objective is not to build the most advanced AI system, but
to demonstrate how you approach ambiguous problems, evaluate technical
trade-offs, and deliver practical solutions.

We are interested in how you think, not just what you build.

### Your Mission

You have recently joined the AI Engineering team at Aurstrat Technology.
Your first responsibility is to help determine the best way to build the
AI Mentor feature.

Three possible implementation strategies have been identified:

- Fine-tuning a Large Language Model
- Retrieval-Augmented Generation (RAG)
- Prompt Engineering using an existing Large Language Model API

Evaluate these approaches and recommend one that best fits the company's
current constraints. The recommendation must be supported by a working
proof of concept — not assumptions.

### Problem Statement

Design and develop a minimal prototype that accepts a 200-word startup idea
submitted by a student and generates structured feedback containing:

- Startup Viability Score
- Key Risks
- Strengths
- Two actionable recommendations for improvement

The prototype demonstrates one implementation approach of your choice.
Beyond building the prototype, justify why the selected approach is the
most appropriate solution for Aurstrat Technology at its current stage.

Business constraints:

- Limited engineering resources
- Near-zero infrastructure budget
- Small development team with limited ML expertise
- MVP expected within two weeks
- Solution must be maintainable as the platform grows

### Deliverables

1. **Working Prototype** — a runnable application or notebook demonstrating
   the chosen approach using at least three different startup ideas.
2. **Architecture Decision Report** — compares Fine-tuning, RAG, and Prompt
   Engineering; explains why the selected approach is the best choice under
   the given constraints.
3. **Failure Analysis** — one realistic scenario where the prototype
   produces poor or misleading feedback: why it failed, potential business
   impact, and how it would be improved in future iterations.

### Technical Constraints

- Use only free-tier APIs or open-source models
- Paid fine-tuning services are not permitted
- Output must be returned in a structured format (JSON or equivalent)
- All implementation decisions must be documented

### Timeline

- Estimated Effort: 6–8 hours
- Submission Deadline: within 5 days

### Submission Format

- GitHub Repository
- Architecture Decision Report (PDF)
- README
- AI Usage Declaration
- Submitted via the Google Form linked above
