---
type: claims-tracker
tier: extension
priority: when-relevant
updated: 2026-04-13
tokens_estimate: 1200
domain: intellectual-property
optional: true
---

<!-- AGENT DIRECTIVES
- This file is OPTIONAL. Only relevant for projects heading toward patent filings.
- Inventors maintain Claims Summary, Prior Art Maps, and Evidence sections.
- Counsel maintains Status, Legal Notes, and Prosecution Timeline.
- Do not modify entries in the Prosecution Timeline without explicit user instruction.
-->

# Claims Tracker

Intellectual property claim development and prosecution tracking.

This file tracks patent claims from initial conception through filing and prosecution. It bridges technical work (documented in PROVENANCE.md and EXPERIMENT_JOURNAL.md) with legal requirements.

**Inventors** maintain: Claims Summary, Prior Art Map, Evidence of Novelty.
**Counsel** maintains: Status, Legal Notes, Prosecution Timeline.
**Both** review Prior Art Maps together before any filing or office action response.

**Last reviewed by counsel:** [Date]
**Last updated by inventors:** [Date]

---

## Claims Summary

<!-- AGENT: This table is the index of all claims. Each claim has a unique ID used for cross-referencing throughout this file and in other context files. When adding a claim, use the next sequential ID. -->

| Claim ID | Title | Type | Novelty Basis | Prior Art Risk | Status | Related |
|----------|-------|------|---------------|----------------|--------|---------|
| [C-001] | [Short descriptive title] | Independent | [What is new] | [High/Medium/Low] | Draft | see PROVENANCE#D-[NNN] |
| [C-002] | [Short descriptive title] | Independent | [What is new] | [High/Medium/Low] | Draft | see PROVENANCE#D-[NNN] |
| [C-003] | [Short descriptive title] | Dependent (on C-001) | [Additional limitation] | [High/Medium/Low] | Draft | see PROVENANCE#D-[NNN] |

**Status values:** Draft > Under Review > Filed > Office Action > Allowed > Granted > Abandoned

*Next claim ID: [C-004].*

---

## Claim Detail Template

Copy this section for each claim. Fill in all fields.

---

### [C-001] [Claim title]

**Type:** Independent
**Status:** Draft
**Priority:** [High / Medium / Low]
**Date conceived:** [YYYY-MM-DD]
**Inventor(s):** [Names]

#### Plain Language

[Write so a patent examiner with a CS degree but no domain specialization understands in 60 seconds.]

**One sentence:** [The version the examiner will remember.]

#### Key Elements

1. [e.g., "A method for [doing X], comprising..."]
2. [e.g., "Each [element] is a typed structure: [fields]"]
3. [e.g., "[Elements] are processed by [step] conditioned on [input]"]

#### Claim Language (Draft)

> A method for [doing X], comprising:
> (a) [first step],
> (b) [second step], and
> (c) [third step],
> wherein [distinguishing limitation].

#### Prior Art Map

| Prior Work | What They Do | How We Differ | Ref |
|-----------|-------------|---------------|-----|
| [Author, Year] | [Their approach] | [Our distinction] | [Link or citation] |
| [Author, Year] | [Their approach] | [Our distinction] | [Link or citation] |

#### Evidence of Novelty

| Type | Description | Location |
|------|-------------|----------|
| Architectural | [How the design differs from prior art] | [File, section, or figure reference] |
| Experimental | [Quantitative result demonstrating the difference] | see EXPERIMENT_JOURNAL#E-[NNN] |
| Implementation | [Working system demonstrating the architecture] | [Source file reference] |

#### Dependent Claims

- [C-001a] ...where [additional limitation narrowing the independent claim].
- [C-001b] ...where [another limitation].

#### Legal Notes (Counsel)

- **102 (anticipation):** [Concerns]
- **103 (obviousness):** [Concerns -- especially "combination of known elements"]
- **Scope notes:** [Broaden / narrow recommendations]

---

### [C-002] [Claim title]

**Type:** Independent
**Status:** Draft
**Priority:** [High / Medium / Low]
**Date conceived:** [YYYY-MM-DD]
**Inventor(s):** [Names]

#### Plain Language

[Plain-language description.]

**One sentence:** [Summary.]

#### Key Elements

1. [Element]
2. [Element]
3. [Element]

#### Claim Language (Draft)

> [Draft claim language following patent conventions.]

#### Prior Art Map

| Prior Work | What They Do | How We Differ | Ref |
|-----------|-------------|---------------|-----|
| [Author, Year] | [Their approach] | [Our distinction] | [Link or citation] |

#### Evidence of Novelty

| Type | Description | Location |
|------|-------------|----------|
| [Type] | [Description] | see EXPERIMENT_JOURNAL#E-[NNN] |

#### Dependent Claims

- [C-002a] ...where [additional limitation].

#### Legal Notes (Counsel)

- **102 (anticipation):** [Concerns]
- **103 (obviousness):** [Concerns]
- **Scope notes:** [Recommendations]

---

*Add new claim details here using the template above. Use the next sequential claim ID.*

---

## Prior Art Map (Global)

Consolidated prior art relevant across multiple claims. Per-claim prior art maps above may reference entries here by Ref ID.

<!-- AGENT: Do not remove prior art entries. If new prior art is discovered, add it with the next sequential ID. If prior art is later found to be irrelevant, change its Status to "Dismissed" with a reason — do not delete it. -->

| Ref ID | Source | Title / Description | Relevant To | Distinction | Status |
|--------|--------|---------------------|-------------|-------------|--------|
| PA-001 | [Patent / Paper / Product] | [Title or short description] | [C-001], [C-002] | [How the claimed invention differs] | Active |
| PA-002 | [Patent / Paper / Product] | [Title or short description] | [C-001] | [How the claimed invention differs] | Active |

*Next prior art ID: PA-003.*

---

## Combination Claim Analysis

If the invention combines known elements in a new way, document why the combination itself is non-obvious.

### Elements vs. Prior Art

| Element | Our Version | Closest Prior Art | Gap |
|---------|------------|-------------------|-----|
| A. [Element] | [Our specifics] | [Closest work] / PA-[NNN] | [What prior art lacks] |
| B. [Element] | [Our specifics] | [Closest work] / PA-[NNN] | [What prior art lacks] |
| C. [Element] | [Our specifics] | [Closest work] / PA-[NNN] | [What prior art lacks] |

### Non-Obviousness Argument

Why a skilled practitioner would not combine these elements unprompted:

1. [Reason -- e.g., "Prior work treats X as Y. We treat X as Z. The artifacts compose differently as a result."]
2. [Reason -- e.g., "Approach A precludes approach B architecturally. Our timing model enables a different class of solution."]
3. [Reason -- e.g., "No prior system creates [specific artifact type] with [specific properties]."]

**Graham v. John Deere factors:**

| Factor | Analysis |
|--------|----------|
| Scope and content of prior art | [Summary of what the prior art teaches. Reference PA-NNN entries.] |
| Differences between claims and prior art | [C-001] differs from PA-001 in [specific difference]. [C-002] differs from PA-002 in [specific difference]. |
| Level of ordinary skill | [Define the hypothetical person -- education, experience, knowledge base.] |
| Secondary considerations | [Unexpected results, commercial success, long-felt need, failure of others, teaching away. Reference EXPERIMENT_JOURNAL#E-[NNN] for experimental evidence.] |

---

## Key Distinctions

Reusable argument blocks for office action responses. Copy-paste into prosecution filings.

<!-- AGENT: These distinctions are the strongest differentiators. Keep them concise and examiner-ready. -->

### [KD-001] [Distinction title -- e.g., "Evaluation Instruments vs. Memory"]

**They** [what prior art does].
**We** [what the claimed invention does differently].

**Examiner analogy:** [Plain-language analogy that makes the distinction intuitive.]

**Distinguishes from:** [List of prior art references this argument addresses.]
**Supports claims:** [C-001], [C-003]
**Evidence:** see EXPERIMENT_JOURNAL#E-[NNN]

### [KD-002] [Distinction title]

**They** [what prior art does].
**We** [what the claimed invention does differently].

**Examiner analogy:** [Analogy.]

**Distinguishes from:** [Prior art references.]
**Supports claims:** [C-002]
**Evidence:** [Reference.]

---

## Prosecution Timeline

<!-- AGENT: Do not modify this section without explicit user instruction. This section is maintained by patent counsel. -->

| Date | Event | Action Taken | Deadline | Notes |
|------|-------|-------------|----------|-------|
| [YYYY-MM-DD] | [e.g., Invention disclosure] | [e.g., Filed with firm] | [Response deadline if any] | [Additional notes] |
| [YYYY-MM-DD] | [e.g., Prior art search] | [e.g., Identified N references] | -- | [Notes] |
| [YYYY-MM-DD] | [e.g., Provisional filed] | [e.g., App No. XX/XXX,XXX] | [12-month non-provisional deadline] | [Notes] |
| [YYYY-MM-DD] | [e.g., Office action received] | [e.g., 103 on Claims 1, 3] | [Response due date] | [Notes] |

---

## Glossary for Counsel

Technical terms used in the claims, defined for non-technical readers.

| Term | Plain English | Technical Definition | Used In |
|------|-------------|---------------------|---------|
| [Term] | [One-sentence lay definition] | [Precise technical definition] | [C-001], [C-002] |
| [Term] | [Lay definition] | [Technical definition] | [C-003] |

---

## Legal Notes

Space for counsel to record strategy notes, examiner comments, or prosecution guidance.

[No entries yet.]

---

## Document History

| Date | Author | Change |
|------|--------|--------|
| [YYYY-MM-DD] | [Name] | Initial tracker created. |
| [YYYY-MM-DD] | [Name] | Prior art map after literature review. |
| [YYYY-MM-DD] | [Counsel] | Legal notes after initial review. |

---

**PRIVILEGED AND CONFIDENTIAL**

This document contains information subject to attorney-client privilege and/or work product doctrine. It was prepared in anticipation of patent prosecution and is not to be disclosed outside the attorney-client relationship without express written consent. Inadvertent disclosure does not constitute waiver of any applicable privilege.

---

*Cross-references: see PROVENANCE.md for decision history underlying claims, EXPERIMENT_JOURNAL.md for experimental evidence supporting novelty and non-obviousness, GLOSSARY.md for general project terminology.*
