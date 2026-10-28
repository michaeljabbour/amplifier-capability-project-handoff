---
type: glossary
tier: 1
priority: always
updated: 2026-04-13
tokens_estimate: 300
---

<!-- AGENT DIRECTIVES
- Read this file at the start of every session alongside PROJECT_CONTEXT.md.
- Use ONLY the terms defined here. Do not introduce synonyms.
- The "Does NOT Mean" column is critical — it prevents misinterpretation.
- If you encounter an undefined term, ask the user to add it here.
-->

# Glossary

Terms chosen deliberately. Prevents agents and collaborators from drifting into synonyms that blur meaning.

## Core Terms

| Term | Means | Does NOT Mean | Example |
|------|-------|---------------|---------|
| [term, e.g., "module"] | [precise definition, e.g., "a single Python package under src/ with its own __init__.py"] | [common misinterpretation, e.g., "any .py file" or "a class"] | [concrete usage, e.g., "src/auth/ is the auth module"] |
| [term, e.g., "deploy"] | [precise definition, e.g., "push to production via CI pipeline"] | [common misinterpretation, e.g., "merge to main" or "run locally"] | [concrete usage, e.g., "we deploy after the smoke tests pass in staging"] |
| [term, e.g., "spike"] | [precise definition, e.g., "a time-boxed investigation that produces a finding, not shipping code"] | [common misinterpretation, e.g., "a prototype" or "a quick hack to ship"] | [concrete usage, e.g., "the Redis spike concluded we should use Valkey instead"] |

## Acronyms

| Acronym | Expansion | Context |
|---------|-----------|---------|
| [e.g., "OA"] | [e.g., "Office Action"] | [e.g., "USPTO correspondence requiring a response"] |
| [e.g., "PR"] | [e.g., "Pull Request"] | [e.g., "GitHub PR, not press release"] |

---

Add terms as they emerge. The cost of a missing definition is rediscovery; the cost of adding one is seconds.
