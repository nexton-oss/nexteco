#!/usr/bin/env python3
"""
NextEco Benchmark Script.

Validates and renders a Markdown report multiple times in sequence to measure
execution time and throughput of the data validation pipelines.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
import logging

from nexteco.model import load_yaml, render_markdown, validate_cost_model

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Main entry point for the benchmark execution script.

    Returns
    -------
    int
        Exit code representing the result of the benchmarking run.
    """
    # Configure the benchmark's CLI argument parser
    parser = argparse.ArgumentParser(
        description="Benchmark NextEco end-to-end validation and Markdown rendering"
    )
    parser.add_argument("input", nargs="?", default="cost_of_running.full.yaml.example")
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Emit a JSON summary")
    args = parser.parse_args()

    # Collectors for individual step timings
    samples_validate: list[float] = []
    samples_render: list[float] = []
    samples_total: list[float] = []

    for _ in range(args.iterations):
        start_total = time.perf_counter()

        # Step 1: Execute validation
        start_validate = time.perf_counter()
        data = load_yaml(args.input)
        validation = validate_cost_model(data)
        samples_validate.append(time.perf_counter() - start_validate)

        # Step 2: Execute rendering
        start_render = time.perf_counter()
        markdown = render_markdown(data)
        samples_render.append(time.perf_counter() - start_render)

        total_elapsed = time.perf_counter() - start_total
        samples_total.append(total_elapsed)

    # Compile the final statistics report dictionary
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
        logger.info(json.dumps(summary, indent=2))
    else:
        for key, value in summary.items():
            logger.info(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
