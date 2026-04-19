# NextEco for AI agents and agentic workflows

NextEco is deliberately compatible with agent-native development.

## Why

Cost-of-running is repetitive enough to benefit from AI assistance, but important enough that the result must remain auditable.

That is why NextEco uses:
- a repository-native YAML source of truth
- validation
- generated Markdown
- benchmark hooks

## Agent role

An agent can help:
- initialize the subsystem
- inspect repo archetypes
- propose a canonical unit of work
- populate assumptions
- benchmark candidate paths using `nexteco measure`
- regenerate documentation

## Human role

A human should still verify:
- pricing provenance
- geography-sensitive carbon assumptions
- measurement quality
- what counts as the canonical unit of work

See [`skill/nexteco/`](skill/nexteco/) for the embedded skill packaging.
