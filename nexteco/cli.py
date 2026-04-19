from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .model import load_yaml, render_markdown, validate_cost_model, write_text
from .templates import get_template_text
import json
from .measure import measure_command


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.output)
    if target.exists() and not args.force:
        print(f"Refusing to overwrite existing file: {target}", file=sys.stderr)
        return 2
    content = get_template_text(args.template)
    write_text(target, content)
    print(f"Wrote {target}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)
    result = validate_cost_model(data)
    for issue in result.issues:
        prefix = "ERROR" if issue.level == "error" else "WARN"
        print(f"{prefix}: {issue.message}")
    if result.is_valid():
        print("Validation passed.")
        return 0
    print("Validation failed.", file=sys.stderr)
    return 1


def cmd_render(args: argparse.Namespace) -> int:
    data = load_yaml(args.input)
    result = validate_cost_model(data)
    markdown = render_markdown(data)
    output = Path(args.output)
    write_text(output, markdown)
    if result.errors:
        print(f"Rendered {output}, but validation errors remain.", file=sys.stderr)
        for issue in result.errors:
            print(f"ERROR: {issue.message}", file=sys.stderr)
        return 1
    for issue in result.warnings:
        print(f"WARN: {issue.message}")
    print(f"Rendered {output}")
    return 0


def cmd_measure(args: argparse.Namespace) -> int:
    cmd_args = args.cmd_args
    if not cmd_args:
        print("ERROR: A command must be provided to measure.", file=sys.stderr)
        return 1
    if cmd_args[0] == "--":
        cmd_args = cmd_args[1:]

    result = measure_command(cmd_args)
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexteco", description="Repository-native cost-of-running tooling"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a starter YAML model")
    init_parser.add_argument("--template", choices=["min", "full"], default="min")
    init_parser.add_argument("--output", default="cost_of_running.yaml")
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=cmd_init)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate a cost model YAML file"
    )
    validate_parser.add_argument("input")
    validate_parser.set_defaults(func=cmd_validate)

    render_parser = subparsers.add_parser(
        "render", help="Render Markdown from a cost model YAML file"
    )
    render_parser.add_argument("input")
    render_parser.add_argument("--output", default="cost_of_running.md")
    render_parser.set_defaults(func=cmd_render)

    measure_parser = subparsers.add_parser(
        "measure",
        help="Measure energy and power profile of a command via native OS tools",
    )
    measure_parser.add_argument(
        "cmd_args", nargs=argparse.REMAINDER, help="The command to run and measure"
    )
    measure_parser.set_defaults(func=cmd_measure)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
