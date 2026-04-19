---
name: nexteco
description: create, validate, improve, and explain repository-native cost-of-running models. use when the user asks to estimate what a codebase costs to run, add or improve cost_of_running.yaml or cost_of_running.md, compare runtime or api scenarios, assess money, time, energy, or carbon per canonical unit of work, or make repository cost estimation reproducible and auditable.
---

# NextEco

Use this skill to turn repository cost estimation into a **small, honest, auditable subsystem**.

## Workflow

1. Identify the repository archetype.
   - For repository patterns, see [references/repo-archetypes.md](references/repo-archetypes.md).
2. Choose one canonical unit of work.
3. Prefer one YAML source of truth and one generated Markdown report.
4. Apply the honesty taxonomy strictly.
   - See [references/honesty-taxonomy.md](references/honesty-taxonomy.md).
5. Validate before rendering.
6. Add a lightweight benchmark path when warranted.
   - See [references/benchmark-patterns.md](references/benchmark-patterns.md).
7. Keep the implementation small.

## Required behavior

- Never invent runtime, hardware, pricing, carbon intensity, or throughput facts.
- Never present estimated values as measured values.
- Prefer the smallest useful subsystem over a large workflow.
- Keep local compute and external API cost separated when both matter.
- Make deployment assumptions visible.

## Output shape

When the repository does not already have an established cost-of-running subsystem, the default target is:

- `cost_of_running.yaml`
- `cost_of_running.md`
- a small validation/render path
- one or two meaningful tests
- a lightweight benchmark entry point

## References

- Methodology: [references/methodology.md](references/methodology.md)
- YAML structure: [references/yaml-schema-guide.md](references/yaml-schema-guide.md)
- Triggering guidance: [references/triggering-guide.md](references/triggering-guide.md)
- Examples: [references/examples.md](references/examples.md)
- External Methodology: 
  - https://calculator.green-algorithms.org 
  - https://calculator.green-algorithms.org/ai

## Scripts

Use these deterministic helpers when useful:

- `nexteco init`
- `nexteco validate`
- `nexteco render`
- `nexteco measure -- <command>` (to benchmark and extract dynamic power metrics)

## Final reminder

An honest placeholder beats a confident lie.
