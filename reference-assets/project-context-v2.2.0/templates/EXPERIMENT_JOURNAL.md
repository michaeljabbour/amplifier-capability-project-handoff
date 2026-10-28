---
type: experiment-journal
tier: 3
priority: when-investigating
updated: 2026-04-13
tokens_estimate: 1000
---

<!-- AGENT DIRECTIVES
- Read this file when debugging, exploring, or running experiments.
- ALWAYS record hypothesis BEFORE running an experiment. No post-hoc storytelling.
- After 10 entries, archive older entries to experiments/archive/ and keep only the Running Summary + last 5 entries in this file.
- Cross-reference decisions in PROVENANCE.md when experiment results inform a decision.
-->

# Experiment Journal

Scientific record of what was tried, what happened, and what it means. Failures are as valuable as successes here.

---

## Rules

1. Log every experiment. Failures especially.
2. Record hypothesis before running. No post-hoc storytelling.
3. Raw numbers in tables. Summaries lie.
4. State what you learned, not just what happened.
5. Link to the commit so anyone can reproduce.

---

## Archival Policy

After 10 entries, move older entries to `experiments/archive/YYYYMM.md`. Keep the Running Summary table and the last 5 entries in this file. This keeps the active file within context window budget while preserving full history.

---

## Entries

### [E-001] [Experiment title: baseline measurement]

| Field  | Value                           |
|--------|---------------------------------|
| Date   | [YYYY-MM-DD]                    |
| Commit | [short hash]                    |
| Run ID | [run identifier, if applicable] |

**Hypothesis:** [What you expected to happen and why. Write this before running.]

**Setup:** [Data used, conditions, model or config, environment. Enough detail to reproduce.]

**Results:**

| Condition         | Metric A | Metric B | Cost    | Time    |
|-------------------|----------|----------|---------|---------|
| [Baseline]        | [value]  | [value]  | [value] | [value] |
| [Variant, if any] | [value]  | [value]  | [value] | [value] |

**Finding:** [1-3 sentences. Was the hypothesis supported? What did the numbers actually show?]

**Next Step:** [What this result tells you to try next.]

---

### [E-002] [Experiment title: follow-up to E-001]

| Field  | Value                           |
|--------|---------------------------------|
| Date   | [YYYY-MM-DD]                    |
| Commit | [short hash]                    |
| Run ID | [run identifier, if applicable] |

**Hypothesis:** Based on the baseline established in [E-001], [what you expected when changing the variable and why].

**Setup:** Same as [E-001] except [specific change made]. See PROVENANCE.md#D-nnn if this was driven by a decision.

**Results:**

| Condition        | Metric A | Metric B | Cost    | Time    |
|------------------|----------|----------|---------|---------|
| [E-001 baseline] | [value]  | [value]  | [value] | [value] |
| [New condition]  | [value]  | [value]  | [value] | [value] |

**Finding:** [1-3 sentences. Compare against E-001 baseline. Was the hypothesis supported?]

**Next Step:** [What this result tells you to try next.]

---

## Enhanced Entry Format

For experiments that warrant deeper analysis, extend entries with the sections below.

### Root Cause Analysis

Use when an experiment reveals a failure or unexpected behavior.

| Failure Mode      | Evidence            | Mechanism           | Fix Applied                 |
|-------------------|---------------------|---------------------|-----------------------------|
| [Name of failure] | [What you observed] | [Why it happened]   | [What you did about it]     |

### Pre-Registered Expectations

Use for high-stakes experiments to prevent hindsight bias.

```
Expected outcome: [precise prediction, written before running]
Confidence: [low / medium / high]
What would change my mind: [specific observation that would falsify the hypothesis]
```

### Stats Plan

Use when statistical rigor matters.

```
Test: [e.g., paired t-test, bootstrap CI]
Sample size: [n]
Significance threshold: [e.g., p < 0.05, CI excludes zero]
Multiple comparisons correction: [method, if applicable]
```

### vs. Expectations

Use after running a pre-registered experiment.

```
Predicted: [what you wrote above]
Observed: [what actually happened]
Delta: [magnitude and direction of surprise]
Interpretation: [what the gap means]
```

---

## Running Summary

| Entry   | Date         | Change                       | Key Result                             | Status     |
|---------|--------------|------------------------------|----------------------------------------|------------|
| [E-001] | [YYYY-MM-DD] | [Baseline measurement]      | [One-line result summary]              | [complete] |
| [E-002] | [YYYY-MM-DD] | [Follow-up variable change] | [One-line result summary, ref E-001]   | [complete] |

---

## Open Questions

1. [Question arising from experiments so far, e.g., "Does the improvement in E-002 hold at larger scale?"]
2. [Question about an unexplained observation, e.g., "Why did Metric B degrade in Condition X?"]
3. [Forward-looking question, e.g., "What is the cost ceiling before the approach becomes impractical?"]
