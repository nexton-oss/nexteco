# Contributing

Thanks for improving NextEco.

## What this project is

NextEco is now both:

- a **small developer tool**
- a **strong agent workflow**
- an **embedded skill for agent environments**

All three matter.

The prompts are important, but the repository must also remain executable, testable, easy to trust, and coherent as a public open-source project.

---

## Project architecture

NextEco exists in two forms inside one main repository:

### 1. OSS repository
This is the public source of truth for:

- the Python package
- the CLI
- templates
- examples
- docs
- tests
- roadmap
- public discussion

### 2. Embedded skill
This lives under:

```text
skill/nexteco/
```

Its purpose is to make the workflow directly executable by Claude-style agents and AI-powered IDEs.

The repository is for humans.  
The skill is for agents.

They should evolve together, not drift apart.

---

## Ground rules

- Keep the tool **small, auditable, and boring**
- Prefer explicit structure over cleverness
- Do not weaken the honesty taxonomy
- Do not add infrastructure that the project will not maintain
- Do not introduce SaaS, telemetry, or lock-in
- Do not let the embedded skill drift away from the OSS doctrine

---

## Non-negotiable principles

A good NextEco change preserves these ideas:

- one canonical unit of work
- one YAML source of truth
- one generated Markdown report
- explicit formulas where relevant
- explicit exclusions where relevant
- strict distinction between:
  - `measured`
  - `estimated`
  - `placeholder`
  - `TODO`

An honest placeholder is better than a confident lie.

---

## Good contributions

Examples of valuable changes:

- improve CLI validation quality
- improve Markdown rendering quality without adding noise
- tighten arithmetic checks
- improve stale pricing detection
- improve starter templates
- improve prompt reliability on real repositories
- improve the embedded skill's triggering or workflow behavior
- add a realistic end-to-end example
- improve tests around sync between YAML and Markdown
- improve docs around methodology, schema, or repo archetypes
- add lightweight CI for tests, example validation, skill packaging, and benchmark smoke checks
- propose cautious release automation once the project surface is stable

---

## Current priorities

1. Make the CLI more useful while keeping it tiny
2. Strengthen the templates and generated report quality
3. Improve reliability for mixed local-compute and external-API systems
4. Keep prompts strong without turning them into sprawling frameworks
5. Keep the embedded skill sharp, useful, and tightly aligned with the OSS repo
6. Preserve honesty and explicit uncertainty everywhere
7. Add lightweight CI for tests, example validation, and skill packaging

---

## What to avoid

Avoid changes that:

- add heavy infrastructure
- turn the tool into a hosted product
- hide uncertainty behind polished wording
- make the prompts longer without making them better
- add complexity that a small OSS maintainer would not keep alive
- duplicate the same doctrine in too many places without a clear sync strategy
- make the skill the “real” product and the repo merely documentation

The repository is the source of truth.  
The skill is a powerful interface to it.

---

## Development

Install in editable mode:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Run the tool locally:

```bash
nexteco validate cost_of_running.full.yaml.example
nexteco render cost_of_running.full.yaml.example --output /tmp/cost_of_running.md
python scripts/benchmark_render.py cost_of_running.full.yaml.example --iterations 5
```

If you are changing the embedded skill, also validate or package it before proposing the change.

---

## Skill-related contributions

Strong skill contributions include:

- better trigger phrasing
- better “when to use / when not to use” behavior
- better references for repository archetypes
- better examples for mixed API/local compute systems
- stronger agent guidance that stays concise
- tighter reuse of shared templates and doctrine

Weak skill contributions include:

- making `SKILL.md` too long
- moving too much knowledge into frontmatter
- adding vague language
- duplicating large parts of the repository docs without reason

The skill should use progressive disclosure well:
- frontmatter for triggering
- `SKILL.md` for core workflow
- `references/` for deeper guidance
- `assets/` for reusable templates

---

## Documentation contributions

Documentation should improve:

- clarity
- precision
- trust
- usability
- contributor understanding

Documentation should not:

- inflate claims
- pretend estimates are measurements
- add marketing fluff at the expense of operational meaning

---

## Testing expectations

A contribution is stronger when it improves or preserves at least one of:

- arithmetic coherence
- structural validation
- YAML/Markdown synchronization
- example reproducibility
- embedded skill packaging quality
- benchmark helper clarity

Not every contribution needs new tests, but changes that affect behavior should be checked.

---

## Pull requests

Open a PR with:

1. the change
2. the concrete problem it solves
3. how you verified it
4. any before/after effect on generated output or developer ergonomics

Small, sharp pull requests are preferred.

---

## Final note

NextEco should feel like a serious engineering artifact, not a theatrical AI wrapper.

Small is good.  
Sharp is good.  
Honest is mandatory.
