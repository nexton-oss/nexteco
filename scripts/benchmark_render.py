#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import time

from nexteco.model import load_yaml, render_markdown, validate_cost_model


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark NextEco end-to-end validation and Markdown rendering"
    )
    parser.add_argument("input", nargs="?", default="cost_of_running.full.yaml.example")
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Emit a JSON summary")
    args = parser.parse_args()

    samples_validate = []
    samples_render = []
    samples_total = []

    for _ in range(args.iterations):
        start_total = time.perf_counter()

        start_validate = time.perf_counter()
        data = load_yaml(args.input)
        validation = validate_cost_model(data)
        samples_validate.append(time.perf_counter() - start_validate)

        start_render = time.perf_counter()
        markdown = render_markdown(data)
        samples_render.append(time.perf_counter() - start_render)

        total_elapsed = time.perf_counter() - start_total
        samples_total.append(total_elapsed)

    summary = {
        "benchmark": "load_validate_render",
        "input": args.input,
        "iterations": args.iterations,
        "validation_passed": validation.is_valid(),
        "generated_markdown_chars": len(markdown),
        "validate_mean_seconds": round(statistics.mean(samples_validate), 6),
        "render_mean_seconds": round(statistics.mean(samples_render), 6),
        "total_mean_seconds": round(statistics.mean(samples_total), 6),
        "total_median_seconds": round(statistics.median(samples_total), 6),
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for key, value in summary.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
