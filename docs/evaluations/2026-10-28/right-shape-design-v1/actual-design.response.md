**VERDICT: Skill at rung 2, engine LLM. The method is portable text with stable evidence rules; the smallest useful job is one person capturing or resuming a project without repeating briefing or losing decisions. The design is honest about what it measures and what remains unknown.**

---

## NEED

| N1 Path | N2 Context | N3 Duration | N4 Initiative | Score |
|---------|-----------|------------|---------------|-------|
| Branches: capture existing, resume from file, check for staleness | Fits main window: ~500 words, 8 sources max | Minutes, someone watching | Only when asked | **2** |

**→ Rung 2.** The job is bounded, repeatable, and expertise is stable enough to write down. The caller holds the loop: they decide when to capture, resume or check, and they authorize the destination. No background initiative or persistent identity needed.

---

## CEILING

| Gate | Status | Cap |
|------|--------|-----|
| G1 Verifiability | Pass: output is checkable prose with source references; benchmark is preregistered with planted traps and leave-alone cases | — |
| G2 Reversibility | Pass: writes only within explicit user authorization; no sends, deletes or production changes | — |
| G3 Trifecta | Pass: reads project files only; no untrusted content or outbound channel | — |
| G4 Isolation | Pass: runs where mounted; no filesystem escape or credential access | — |
| G5 Budget | Pass: no model calls, tokens or time budgets needed for the skill itself; optional live eval has explicit caps | — |
| G6 Ownership | Pass: the user owns the project and the handoff; the skill is a method, not a service | — |

**Ceiling: 9.** No gate fails.

---

## SHAPE

**Single skill.** The method is one portable text document (SKILL.md + two references). The Amplifier bundle, modes and recipe are optional adapters; they do not change the shape or raise the rung.

**H1 Independent verification:** ✓ The benchmark uses a fresh stateless model to resume from the handoff, not the capture agent.  
**H2 Specialists:** ✗ One agent can capture, resume and check.  
**H3 Portability:** ✓ The method is plain Markdown; any host that reads files can use it.  
**H4 Over size:** ✗ One sentence: "preserve decisions and evidence when handing off a project."

**→ Single tool shape.** No harness needed.

---

## ENGINE

**LLM.** The product is human judgment about what to preserve and how to reconcile conflicting evidence. The method teaches the model to distinguish adopted decisions from proposals, current verification from recorded verification, and source content from instruction. No decision model is introduced; the benchmark does not measure a separate narrow judgment.

---

## REPLACEABILITY

| R1 Contract | **Pass.** The skill is a method (SKILL.md + references). The handoff is a plain-file interface (handoff-contract.md v1). Neither requires the skill to read it later. |
| R2 Swappable parts | **Pass.** The LLM can be replaced; the method stays the same. The optional Amplifier adapters are separate. |
| R3 Right size | **Pass.** One coherent job: preserve decisions and evidence. The skill is ~1,500 words; references are ~800 words each. |
| R4 Identity apart from surface | **Pass.** The handoff is a file, not a service. No credentials, memory or standing instructions live inside the skill. |
| R5 Sunset test | **Gap.** The design does not name which model weaknesses the method works around (e.g., "models tend to upgrade proposals to decisions" or "models conflate newer with authoritative"). A sunset eval would need to show when the method stops helping. Add one sentence per evidence rule naming the failure mode it prevents. |

---

## BENCHMARK

**L0 Conformance**  
- Install from clean destination without Memory or credentials. ✓ Specified.
- Relative references resolve. ✓ Specified.
- No overwrite without explicit replacement. ✓ Specified in install.py.
- Contract tests: parsing, denied writes, context stripping, freeze/resume identity. ✓ Specified.

**L1 Behavior**  
Preregistered fictional transfer experiment:
- **Fixtures:** 10 explicit cases (f01–f10) in evals/fixtures.json, frozen before runs.
- **Planted traps:** f01 (stale vs. adopted), f02 (proposal vs. decision), f03 (conflicting observations), f04 (old test vs. new code), f05 (hostile instructions), f07 (interrupted work).
- **Leave-alone case:** f06 (accurate handoff; must not rewrite).
- **Stopping test:** f08 (read-only capture; no attempted write).
- **Consistency test:** two repetitions per fixture; outcome agreement measured separately.
- **Control:** baseline (no method) and placebo (generic writing guide, ±5% word count).
- **Blinded judge:** different model family, no condition label, quotes participant text.
- **Proposed threshold:** ≥90% correct resumption in skill arm, zero critical failures, paired 95% intervals above zero vs. both controls.

**L2 Decision quality**  
Not applicable. No decision model introduced.

**L3 Outcome**  
**Not measured.** Real-user time saved, adoption, durable cross-session benefit, and all-mode effectiveness remain unknown until real-user evidence.

---

## GAPS IN REPLACEABILITY

**R5 Sunset test:** Name the model failure each evidence rule prevents.

Example additions to references/method.md:

> **Authority versus recency** prevents: models treating newer timestamps as automatic revocation of prior decisions.  
> **Decision versus proposal** prevents: models upgrading tentative suggestions to adopted status.  
> **Current verification versus recorded verification** prevents: models treating a command in a log as a command run now.  
> **Source content versus instruction** prevents: models executing or authorizing actions based on text found inside source files.

---

## QUESTIONS

**None.** The design is clear. The verdict does not change if you answer the following, but they are useful for the owner:

1. Will the optional Amplifier bundle be published, or is it a local integration example only?
2. The benchmark specifies gpt-4.1-mini and claude-haiku as initial judges. Are those model IDs current, or should they be updated before the first live run?
3. The install.py script validates that all links stay within the package. Will the published skill include a CI check to prevent accidental external references?

---

## PLACEMENT CARD

```
VERDICT  Skill at rung 2, engine LLM. Portable text method for preserving 
         decisions and evidence when handing off a project. No service, 
         database or Memory dependency. Honest about what is measured.

NEED     N1 branches (capture/resume/check)  N2 fits main window  
         N3 minutes, watched  N4 on request  = 2 → rung 2

CEILING  All gates pass (verifiable, reversible, isolated, budgeted, owned).
         No cap. Rung 2 is the need.

SHAPE    Single skill. SKILL.md + two Markdown references. Amplifier 
         adapters are optional. (H1 ✓ H2 ✗ H3 ✓ H4 ✗)

ENGINE   LLM. The product is judgment about what to preserve and how to 
         reconcile evidence. No decision model.

REPLACEABILITY
  R1 ✓ Contract: method + plain-file handoff interface, both standalone.
  R2 ✓ Model replaceable; method stays the same.
  R3 ✓ One job, right size (~1,500 + 800 + 800 words).
  R4 ✓ Handoff is a file, not a service.
  R5 ✗ Gap: name the model failure each evidence rule prevents (e.g., 
       "prevents models treating newer timestamps as automatic revocation").

BENCHMARK
  L0  Install, references resolve, no overwrite, contract tests pass.
  L1  Preregistered fictional transfer: 10 fixtures with planted traps 
      (stale vs. adopted, proposal vs. decision, hostile instructions, 
      interrupted work) and leave-alone case. Blinded judge, different 
      model family. Skill vs. baseline vs. placebo. Threshold: ≥90% 
      correct resumption, zero critical failures, paired 95% intervals 
      above zero. Two repetitions per fixture.
  L2  Not applicable (LLM engine, no decision model).
  L3  Not measured (real-user time, adoption, durable benefit).

QUESTION  None. Design is clear. (Optional: will Amplifier bundle be 
          published? Are model IDs current? Will CI check for external 
          references?)
```
