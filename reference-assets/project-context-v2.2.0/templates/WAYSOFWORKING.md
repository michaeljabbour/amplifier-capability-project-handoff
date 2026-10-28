---
type: ways-of-working
tier: 2
priority: session-start
updated: 2026-04-13
tokens_estimate: 1000
---

<!-- AGENT DIRECTIVES
- Read this file at the start of every work session.
- Follow the Session Loop in order. Do not skip steps.
- Check Failure Patterns before debugging — the problem may already be documented.
- If you discover a new failure pattern, add it to this file before finishing.
- If you are confused or stuck, follow the Error Recovery Protocol.
-->

# Ways of Working

Operational playbook. How work gets done in this project.

---

## Session Loop

Every work session follows this sequence. Do not skip steps.

```
Orient  -->  Plan  -->  Execute  -->  Verify  -->  Record
```

| Step | Action | Output |
|------|--------|--------|
| **Orient** | Read PROJECT_CONTEXT.md, GLOSSARY.md, HANDOFF.md (latest entry), and this file. Understand current state before touching anything. | Mental model of where the project stands. |
| **Plan** | State what you intend to do and why. List the files you expect to create or modify. If the plan involves more than 3 files, write it out explicitly. | A short plan (can be a comment, can be in chat). |
| **Execute** | Do the work. Follow Proven Workflows below when applicable. One logical change at a time. | Modified or created files. |
| **Verify** | Run the verification steps in the Verification section below. Confirm outputs match expectations. | Evidence that the change works. |
| **Record** | Update HANDOFF.md with what you did, what changed, and what comes next. Update PROVENANCE.md if a decision was made. | Updated context files. |

<!-- AGENT: If you are resuming a session, the Orient step includes reading the most recent HANDOFF.md entry to understand what the previous session left unfinished. -->

---

## Agent Checklist

### Before Starting

- [ ] Read PROJECT_CONTEXT.md for current state
- [ ] Read GLOSSARY.md for term definitions
- [ ] Read HANDOFF.md (latest entry) for continuity
- [ ] Read this file (WAYSOFWORKING.md) for operational rules
- [ ] Read STRUCTURE.md if creating or moving files

### During Work

- [ ] Follow the relevant Proven Workflow if one exists
- [ ] Check Failure Patterns before debugging an error
- [ ] Make one logical change at a time
- [ ] Do not modify files outside the current task scope without stating why

### After Finishing

- [ ] Run all verification steps
- [ ] Update HANDOFF.md with session summary
- [ ] Update PROVENANCE.md if a decision was made (see PROVENANCE#D-[NNN])
- [ ] Update PROJECT_CONTEXT.md if project state changed

---

## Proven Workflows

Tested sequences that produce reliable results. Follow these exactly when they apply.

<!-- AGENT: When a workflow matches your current task, follow its steps in order. Do not reorder or skip steps. If a step fails, check Failure Patterns before improvising. -->

### [W-001] [Workflow name -- replace with actual]

**When to use:** [Describe the situation that calls for this workflow.]

**Steps:**

```bash
# Step 1: [Description]
[command or action]

# Step 2: [Description]
[command or action]

# Step 3: [Description]
[command or action]

# Step 4: Verify
[verification command]
```

**Why this order:** [Explain why the steps must happen in this sequence. What breaks if you reorder them.]

---

### [W-002] [Workflow name -- replace with actual]

**When to use:** [Describe the situation that calls for this workflow.]

**Steps:**

```bash
# Step 1: [Description]
[command or action]

# Step 2: [Description]
[command or action]

# Step 3: [Description]
[command or action]

# Step 4: Verify
[verification command]
```

**Why this order:** [Explain why the steps must happen in this sequence. What breaks if you reorder them.]

---

*Add new workflows here as they are discovered and validated. Use the next sequential ID: [W-003].*

---

## Failure Patterns

Known problems and their fixes. Check here before debugging from scratch.

<!-- AGENT: Before attempting to fix any error, search this section for matching symptoms. If you find a match, apply the documented fix. If you encounter a new failure pattern, add it here using the next sequential ID before ending your session. -->

### [F-001] [Failure name -- replace with actual]

**Symptom:** [What you observe -- error message, unexpected output, silent failure.]

**Root cause:** [Why it happens.]

**Fix:**

```
# Broken:
[code or command that produces the error]

# Working:
[corrected code or command]
```

**Related:** [Cross-reference if applicable, e.g., "see PROVENANCE#D-003", "see [W-001] step 2".]

---

### [F-002] [Failure name -- replace with actual]

**Symptom:** [What you observe -- error message, unexpected output, silent failure.]

**Root cause:** [Why it happens.]

**Fix:**

```
# Broken:
[code or command that produces the error]

# Working:
[corrected code or command]
```

**Related:** [Cross-reference if applicable.]

---

*Add new failure patterns here as they are discovered. Use the next sequential ID: [F-003].*

---

## Verification

Run these checks after every significant change. All must pass before recording the session.

<!-- AGENT: Do not skip verification. If a check fails, fix the issue before updating HANDOFF.md. If you cannot fix it, document it as a known issue in HANDOFF.md. -->

| Check | Command | Expected Output |
|-------|---------|-----------------|
| Tests pass | `[test command, e.g., pytest src/tests/]` | All tests green, zero failures. |
| Linting clean | `[lint command, e.g., ruff check src/]` | No errors. Warnings acceptable only if pre-existing. |
| Output matches | `[comparison command or manual inspection]` | Output is consistent with previous version or matches specification. |
| Context files current | Review PROJECT_CONTEXT.md, HANDOFF.md | Reflect the actual state after this session. |

Any failure: stop, diagnose root cause, fix, re-run from the top. See Error Recovery Protocol below.

---

## Error Recovery Protocol

When confused or stuck, follow this protocol exactly.

```
1. Stop. Do not make random changes.
2. State what you expected vs what happened.
3. Check Failure Patterns above — is this a known issue?
4. If known: follow the documented fix.
5. If unknown: form a hypothesis, test it, document the result.
6. If stuck after 2 attempts: stop and ask the user.
7. If the user is unavailable: document the issue in HANDOFF.md
   and move to a different task.
```

<!-- AGENT: This protocol exists because the most common agent failure mode is thrashing — making random changes in response to errors without forming a hypothesis. Step 1 (stop) is the most important step. If you find yourself in a fix-retry loop, you have skipped step 1. -->

---

## Environment

| Property | Value |
|----------|-------|
| Language / runtime | [e.g., Python 3.12] |
| Package manager | [e.g., uv, pip, npm] |
| Virtual environment | [e.g., .venv/ -- activate with `source .venv/bin/activate`] |
| Key dependencies | [List critical packages and versions] |
| OS / platform notes | [Any platform-specific considerations] |

<!-- AGENT: If you need to install a dependency, use the package manager listed here. Do not use a different package manager without explicit user instruction. -->

---

## Git Conventions

| Convention | Rule |
|------------|------|
| Commit messages | Imperative mood, present tense. Example: `Add parser for CSV input` |
| Branch naming | `feature/{short-description}`, `fix/{short-description}`, `experiment/{short-description}` |
| Commit scope | One logical change per commit. Do not bundle unrelated changes. |
| Before committing | Run verification checks above. Do not commit failing code. |
| Context files | Always commit context file updates in the same commit as the code they describe. |

---

## Lessons Learned

### What Works

- [Record things that reliably produce good results.]
- [Example: "Running the full test suite before modifying core/ catches regressions early."]
- [Example: "Writing the PROVENANCE entry before implementing the decision clarifies thinking."]

### What Does Not Work

- [Record things that have been tried and failed.]
- [Example: "Modifying data/raw/ files directly -- always copy to data/processed/ first."]
- [Example: "Skipping the Orient step -- leads to duplicate work or conflicting changes."]

---

*Cross-references: see STRUCTURE.md for file placement rules, HANDOFF.md for session continuity, PROVENANCE.md for decision records.*
