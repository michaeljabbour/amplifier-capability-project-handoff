---
mode:
  name: handoff
  shortcut: handoff
  description: "Capture, resume or check one project handoff, preserving decisions and evidence."
  tools:
    safe: [read_file, grep, glob, load_skill, recipes]
    warn: [bash, delegate]
  default_action: allow
---

Load `project-handoff` once and follow its canonical method. Respect the user's existing scope and writing authorization. Return one reviewable handoff or resume brief, then stop. Resuming does not authorize implementation. Do not load unrelated project data or add a Memory dependency. Use `/mode off` when finished.
