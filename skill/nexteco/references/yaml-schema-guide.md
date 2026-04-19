# YAML schema guide

## Core idea

`cost_of_running.yaml` is the machine-readable source of truth.
`cost_of_running.md` is derived from it.

## Typical top-level structure

```yaml
date_updated: "2026-04-19"
canonical_unit_of_work:
  name: "one API request"
  description: "Representative request path"
  status: "estimated"
deployment:
  provider: "aws"
  region: "eu-west-3"
assumptions: {}
scenario: {}
```

## Canonical unit of work

This should be concrete, singular, and reviewable.
Avoid vague labels like "general usage".

## Deployment

Use deployment to record the context that materially affects money, energy, and carbon.

## Assumptions

Assumptions should be explicit and should usually carry:

- `value`
- `unit`
- `status`
- optional `notes`
- optional provenance metadata

## Scenarios

Use a single `scenario` for a  model.
Use `scenarios` when the repo truly benefits from multiple cases.

## Totals

If totals are included, they should be arithmetic consequences of the visible inputs whenever possible.

## Common mistakes

- missing status fields
- implicit deployment assumptions
- invented API pricing
- totals that do not match subtotals
- using Markdown as the primary source of truth
