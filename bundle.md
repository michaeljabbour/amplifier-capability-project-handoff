---
bundle:
  name: project-handoff
  version: 0.1.0
  description: "A portable handoff method with optional Amplifier skill, mode and capture recipe. No Memory dependency."
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main#subdirectory=bundles/anchors/bundle.md
  - bundle: project-handoff:behaviors/project-handoff
---

@anchors:context/system.md
