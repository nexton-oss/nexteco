# Benchmark patterns

## Goal

A NextEco benchmark should help maintainers measure the canonical unit of work without turning the repository into a benchmarking lab.

## Good benchmark traits

- deterministic enough to rerun
- small enough to keep
- obvious command line
- visible output
- connected to the chosen unit of work

## Acceptable benchmark outputs

- wall-clock timing
- stage timing
- benchmark summary file
- lightweight JSON or Markdown summary

## Good enough versus perfect

Perfect realism is not always available.
A lightweight benchmark scaffold is better than pretending exact measurement happened.

## Examples

### CLI

```bash
nexteco measure -- python -m mytool --input fixtures/sample.json
```

### API service

```bash
nexteco measure -- pytest tests/benchmarks/test_request_path.py -q
```

### NextEco itself

```bash
nexteco measure -- python scripts/benchmark_render.py cost_of_running.full.yaml.example --iterations 20
```
