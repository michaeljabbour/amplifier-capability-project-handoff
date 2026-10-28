---
type: structure
tier: 2
priority: when-creating-files
updated: 2026-04-13
tokens_estimate: 800
---

<!-- AGENT DIRECTIVES
- Read this file before creating or moving any files.
- If you add a file or directory, update the Layout section.
- Use the "What Goes Where" table to determine file placement.
- Follow naming conventions exactly — no improvisation.
-->

# Structure

Project directory layout, naming conventions, and file routing.

---

## Principles

| ID | Principle | Meaning |
|----|-----------|---------|
| [S-001] | Self-contained iterations | Each version directory holds everything needed to reproduce its output. No version depends on mutable state from another. |
| [S-002] | One source of truth | Every category of artifact has exactly one canonical location. Duplicating files across directories is a defect. |
| [S-003] | Clean separation | Source code, data, outputs, documentation, and experiments occupy distinct subtrees. They connect through references, not co-location. |

---

## Layout

```
project/
├── src/                          # Source code
│   ├── core/                     # Business rules, algorithms
│   ├── integrations/             # External service connectors
│   ├── utils/                    # Shared utilities
│   └── tests/                    # Test suite (mirrors src/ structure)
├── docs/                         # Design and decision documents
│   ├── design/                   # Architecture, API specs, schemas
│   └── decisions/                # Decision records
├── data/                         # Input data
│   ├── raw/                      # Unmodified source data
│   └── processed/                # Cleaned / transformed data
├── outputs/                      # Generated artifacts (versioned)
│   └── v{N}/                     # Self-contained version output
├── experiments/                  # Experiment scripts and results
├── PROJECT_CONTEXT.md            # Tier 1: Current state
├── GLOSSARY.md                   # Tier 1: Terminology
├── STRUCTURE.md                  # Tier 2: This file
├── WAYSOFWORKING.md              # Tier 2: Operational playbook
├── HANDOFF.md                    # Tier 2: Session continuity
├── PROVENANCE.md                 # Tier 3: Decision journal
├── EXPERIMENT_JOURNAL.md         # Tier 3: Scientific record
└── CLAIMS_TRACKER.md             # Extension: IP tracking (optional)
```

<!-- AGENT: If the actual project layout diverges from this tree, update this section immediately. This diagram is the canonical reference. -->

---

## What Goes Where

| You have... | Put it in... | Reason |
|---|---|---|
| A new algorithm or business rule | `src/core/` | Core logic is isolated from integration and utility concerns. See [S-003]. |
| A connector to an external API or service | `src/integrations/` | External dependencies change independently from core logic. |
| A helper function used by multiple modules | `src/utils/` | Shared utilities avoid duplication across core and integrations. See [S-002]. |
| A unit or integration test | `src/tests/` | Tests mirror `src/` structure. A test for `src/core/parser.py` goes in `src/tests/core/test_parser.py`. |
| An architecture diagram or API spec | `docs/design/` | Design artifacts are long-lived references, not session-specific. |
| A decision record (why we chose X over Y) | `docs/decisions/` | Decision records live near design docs. Cross-reference from PROVENANCE.md. See PROVENANCE#D-[NNN]. |
| Raw input data (CSV, JSON, images) | `data/raw/` | Raw data is immutable. Never modify files in this directory. |
| Cleaned or transformed data | `data/processed/` | Transformations are reproducible; processed data can be regenerated from raw. |
| Final output from a pipeline run | `outputs/v{N}/` | Each version is self-contained. See [S-001]. |
| An experiment script or one-off analysis | `experiments/` | Experiments are exploratory. Promote to `src/` only when proven. Log in EXPERIMENT_JOURNAL.md. |
| A project-level context file | Project root | Tier 1-3 context files and extensions live at the root. See Layout above. |

<!-- AGENT: If a file type is not listed here, ask the user before creating it. Do not invent new top-level directories. -->

---

## Naming Conventions

### Versions

All versioned output uses the format `v{N}` where N is a monotonically increasing integer.

```
outputs/v1/
outputs/v2/
outputs/v3/
```

Do not use date-based version names. Do not skip version numbers.

### Files

| Convention | Example | Notes |
|---|---|---|
| Source files | `snake_case.py`, `snake_case.ts` | Lowercase, underscores. No spaces, no hyphens in source. |
| Test files | `test_{module}.py` | Prefix with `test_`. Mirror the module path. |
| Design documents | `kebab-case.md` | Lowercase, hyphens. Stored in `docs/design/`. |
| Decision records | `DR-{NNN}-{short-title}.md` | Sequential numbering. Stored in `docs/decisions/`. Cross-reference in PROVENANCE.md. |
| Project context files | `UPPER_CASE.md` | Root-level coordination files. |
| Data files | `{descriptive-name}.{ext}` | Use clear names. Include date only if the data is a time-series snapshot. |

### Experiment Runs

Experiment directories use the format `exp-{NNN}-{short-description}/`:

```
experiments/exp-001-baseline-model/
experiments/exp-002-feature-ablation/
experiments/exp-003-hyperparameter-sweep/
```

Each experiment directory should contain its own README or be logged in EXPERIMENT_JOURNAL.md.

---

## Adding a New Version

```bash
# 1. Determine the next version number
ls outputs/

# 2. Create the version directory
mkdir -p outputs/v{N}

# 3. Run the pipeline, directing output to the new directory
#    (project-specific command goes here)

# 4. Verify the output is self-contained
ls outputs/v{N}

# 5. Update context files
#    - PROJECT_CONTEXT.md: set current version
#    - PROVENANCE.md: record the decision that prompted this version
```

<!-- AGENT: After creating a new version, always update PROJECT_CONTEXT.md to reflect the current version number. Cross-reference the version in PROVENANCE#D-[NNN] if it corresponds to a decision. -->

---

## Git Tracking

### Tracked

- All files in `src/`
- All files in `docs/`
- All context files at the project root (`.md` files)
- Experiment scripts in `experiments/`
- Small, representative data samples in `data/raw/` (if under size threshold)

### Ignored (add to `.gitignore`)

```gitignore
data/raw/*.csv
data/raw/*.json
data/processed/
outputs/
experiments/*/results/
*.pyc
__pycache__/
.env
```

<!-- AGENT: If you create a new file type that should be ignored, update .gitignore and note the change in the session's HANDOFF.md entry. -->

---

*Cross-references: see WAYSOFWORKING.md for operational workflows, PROVENANCE.md for decision history, PROJECT_CONTEXT.md for current state.*
