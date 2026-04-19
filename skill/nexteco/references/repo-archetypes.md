# Repository archetypes

## Why archetypes matter

Different repositories deserve different canonical units of work.
NextEco should not behave the same way for every codebase.

## CLI tools

Typical unit:
- one representative command execution

## APIs and services

Typical unit:
- one representative request
- one transaction
- one job handled by the service

## Inference repositories

Typical unit:
- one inference
- one batch of inferences

Split carefully between local compute and remote API usage when both exist.

## Training repositories

Typical unit:
- one training run
- one epoch
- one fine-tuning job

Training repos often benefit from stronger assumptions and clearer exclusions.

## ETL and data pipelines

Typical unit:
- one pipeline execution
- one scheduled batch
- one data refresh

## Frontend applications

Typical unit:
- one build
- one representative user flow
- one rendering pipeline job

## Monorepos

Choose one primary unit of work.
Document the others as out of scope unless the repository genuinely needs a broader model.

## Mixed local-compute plus paid-API systems

This is a highly relevant archetype for modern AI systems.
Always keep the split visible.
