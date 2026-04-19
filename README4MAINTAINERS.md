# NextEco for maintainers

This guide is for maintainers who want to make cost-of-running part of normal repository hygiene.

## What you are maintaining

A small subsystem:
- `cost_of_running.yaml` as the source of truth
- `cost_of_running.md` as the readable generated artifact
- validation rules that protect coherence
- benchmark scripts that keep the numbers tied to real executions

## Maintainer workflow

```bash
nexteco validate cost_of_running.yaml
nexteco render cost_of_running.yaml --output cost_of_running.md
python scripts/benchmark_render.py cost_of_running.yaml --iterations 10
pytest
```

## What good maintenance looks like

- update `date_updated`
- refresh external pricing provenance
- keep measured and estimated values clearly separated
- treat stale pricing as a warning signal
- review changes to assumptions with the same seriousness as code changes

## Good pull request checklist

- Does the canonical unit of work still match the real system?
- Did assumptions change?
- Are benchmark paths still meaningful?
- Are totals still coherent?
- Does the report stay readable for non-authors?
