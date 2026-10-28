# Agent Instructions

This project uses a coordination file system in `project-context/`. These files give you persistent memory across sessions. **Read them before starting any work.**

## Starting a Session

Read these files in order:

1. `project-context/PROJECT_CONTEXT.md` — current project state, phase, team
2. `project-context/GLOSSARY.md` — terminology (use these terms exactly)
3. `project-context/HANDOFF.md` — what happened last session, what to do next

Also read when relevant:

- `project-context/STRUCTURE.md` — before creating or moving files
- `project-context/WAYSOFWORKING.md` — for workflows, failure patterns, verification steps
- `project-context/PROVENANCE.md` — to understand why a decision was made
- `project-context/EXPERIMENT_JOURNAL.md` — to see what was tried and learned

## Ending a Session

Update `project-context/HANDOFF.md` with:

- What you accomplished (specific files, decisions, results)
- What's blocked or unresolved
- What the next session should start with
- Non-obvious context the next agent needs

## Continuous Improvement

As you work, keep the coordination files accurate. This is not extra work — it is part of the work.

| When you... | Update |
|-------------|--------|
| Use a term not in the glossary | `project-context/GLOSSARY.md` — add with "Means" and "Does NOT Mean" |
| Make a design or architecture decision | `project-context/PROVENANCE.md` — context, alternatives, rationale |
| Hit an error and find the fix | `project-context/WAYSOFWORKING.md` — named pattern: symptom, cause, fix |
| Discover a better workflow | `project-context/WAYSOFWORKING.md` — add or update proven workflow |
| Create or move files | `project-context/STRUCTURE.md` — update layout tree and routing table |
| Run an experiment or benchmark | `project-context/EXPERIMENT_JOURNAL.md` — hypothesis first, then results |
| Change the project phase or milestone | `project-context/PROJECT_CONTEXT.md` — update current state |
| Finish any session | `project-context/HANDOFF.md` — see "Ending a Session" above |

**The rule:** If you learned something that would save the next session time, write it down.

## What Not to Do

- Do not modify files inside `project-context/templates/` — those are the versioned source of truth
- Do not create coordination files outside `project-context/` — add to existing files
- Do not skip updates because "it's a small change" — small changes compound
- Do not add speculative entries — only document what actually happened
