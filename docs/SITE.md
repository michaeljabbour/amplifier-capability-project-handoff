# Project Handoff static guide

The local guide follows the family theme used by Right Shape, Taste × Elegance, Market Fit and Worth Using. Its main artifact is a handoff sheet: one fictional brief, an original record and a checked resumption, with the supplied evidence kept beside it. The interactive answer check is a local authored exercise, never a claim of model evaluation or user benefit.

The cream/ink paper, Georgia headings, Arial body and family masthead are retained. Deep teal marks the checked resumption; the original record stays visible. There are no external fonts, runtime dependencies, analytics or network calls. `site/theme/LICENSE` retains the theme's MIT notice. The visual family does not imply institutional affiliation.

## Sources, not a second method

- `site/template.html` provides presentation only.
- `site/site.json` holds metadata and explicitly fictional walkthroughs.
- The build reads the skill's mode table and bounded pass from `skills/project-handoff/SKILL.md`.
- It renders the record from `skills/project-handoff/references/handoff-contract.md` and the benchmark from `docs/BENCHMARK.md`.
- The visible skill source and portable ZIP match the canonical folder byte for byte. The raw text download uses the name `project-handoff-skill.md`, so generated files do not add another source file named `SKILL.md`.

## Build and inspect

```sh
python3 scripts/build.py
python3 scripts/check.py
node --check site/site.js
python3 -m http.server 8770 --bind 127.0.0.1 --directory _site
```

Open the local server and inspect both desktop and phone widths. The first fictional example is readable without JavaScript. Visible labels, native controls, focus styles and reduced-motion support remain in the page; the interaction never sends the supplied example or a visitor's choice to a service.

The page's restrictive content policy permits local assets only and disallows network connections. The Copy prompt button uses the browser clipboard on a secure origin; if it is unavailable, the prompt is selected for the normal Copy command.

## Showing a recorded evaluation

`site/site.json` explicitly selects `docs/evaluations/2026-10-28/study-1/summary.json`. The page shows its provisional three-condition automatic counts, ungraded judgment, disputed critical flags and descriptive intervals alongside the quality review. It reports no credible effectiveness conclusion or advantage over baseline. Passing automatic labels are not presented as validated outcomes.

For another reviewed record, explicitly select its dated summary and rebuild. Supported status labels are `live-pilot`, `live-study`, `offline-smoke` and `blocked`; no automatic search for a flattering record occurs. A pilot stays a pilot; offline and blocked records cannot become behavioral results. Retained study files, including frozen snapshots and raw outputs, export byte for byte. The checker treats frozen prompt Markdown as archived data with its original source-relative links, rather than rewriting it into navigation documentation.

The panel links the frozen report, study semantic review, pilot spot review, local validation and Right Shape application record. Those reviews contain real failures and disputed judgments; they are not passing certifications. The independent four-file skill archive remains separate from all benchmark/provider machinery.

Real-user time saved and durable cross-session benefit stay not measured until evidence supports them, regardless of fictional benchmark performance. Publication is separate from this local build and has not been performed by the builder.
