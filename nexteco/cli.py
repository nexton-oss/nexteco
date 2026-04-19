"""
NextEco Command Line Interface.

This module provides the main entry points for initializing, validating,
rendering, and measuring cost of running data interactively via the CLI.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .model import load_yaml, render_markdown, validate_cost_model, write_text
from .templates import get_template_text
import json
from .measure import measure_command
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def cmd_init(args: argparse.Namespace) -> int:
    """
    Initialize a starter YAML cost model.

    Parameters
    ----------
    args : argparse.Namespace
        The command-line arguments containing `output`, `force`, and `template`.

    Returns
    -------
    int
        Exit code: 0 for success, 2 for refusing to overwrite without force.
    """
    # Resolve the destination file target
    target = Path(args.output)
    
    # Prevent overwriting an existing file unless the user forces initialization
    if target.exists() and not args.force:
        logger.error(f"Refusing to overwrite existing file: {target}")
        return 2
    # Retrieve the raw text for the requested template type ('min' or 'full')
    content = get_template_text(args.template)
    
    # Write the template to the destination target file
    write_text(target, content)
    logger.info(f"Wrote {target}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """
    Validate a cost model YAML file against the conceptual schema.

    Parameters
    ----------
    args : argparse.Namespace
        The command-line arguments containing the `input` path.

    Returns
    -------
    int
        Exit code: 0 if validation is successful, 1 if failures occur.
    """
    # Load the YAML contents into a raw dictionary
    data = load_yaml(args.input)
    
    # Analyze the data with the integrated validation rules
    result = validate_cost_model(data)
    
    # Iterate through and log any accumulated issues from the validation phase
    for issue in result.issues:
        if issue.level == "error":
            logger.error(f"{issue.message}")
        else:
            logger.warning(f"{issue.message}")
    if result.is_valid():
        logger.info("Validation passed.")
        return 0
    logger.error("Validation failed.")
    return 1


def cmd_render(args: argparse.Namespace) -> int:
    """
    Render a Markdown report from a cost model YAML file.

    Parameters
    ----------
    args : argparse.Namespace
        The command-line arguments containing the `input` and `output` paths.

    Returns
    -------
    int
        Exit code: 0 on successful render, 1 if the model contains validation errors.
    """
    # Load the YAML content and ensure it is structured appropriately
    data = load_yaml(args.input)
    
    # Perform strict validation before rendering
    result = validate_cost_model(data)
    
    # Generate the Markdown representation string
    markdown = render_markdown(data)
    # Write output Markdown to the requested target file
    output = Path(args.output)
    write_text(output, markdown)
    
    # Halt on any hard validation errors even though rendering technically succeeded
        logger.error(f"Rendered {output}, but validation errors remain.")
        for issue in result.errors:
            logger.error(f"{issue.message}")
        return 1
    for issue in result.warnings:
        logger.warning(f"{issue.message}")
    logger.info(f"Rendered {output}")
    return 0


def cmd_measure(args: argparse.Namespace) -> int:
    """
    Measure the energy and power profile of an arbitrary shell command.

    Parameters
    ----------
    args : argparse.Namespace
        The command-line arguments containing `cmd_args`.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on argument failure.
    """
    cmd_args = args.cmd_args
    # A positional argument referencing the target command is strictly required
    if not cmd_args:
        logger.error("ERROR: A command must be provided to measure.")
        return 1
    # Ignore the optional `--` double separator used to disambiguate tool flags
    if cmd_args[0] == "--":
        cmd_args = cmd_args[1:]

    # Proxy the target command with the OS-specific hardware measurement profiler
    result = measure_command(cmd_args)
    
    # Dump metrics as JSON for standardized script piping and programmatic access
    logger.info(json.dumps(result.to_dict(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """
    Construct the command-line argument parser for nexteco.

    Returns
    -------
    argparse.ArgumentParser
        The populated argument parser instance for the CLI.
    """
    # Create the root parser
    parser = argparse.ArgumentParser(
        prog="nexteco", description="Repository-native cost-of-running tooling"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # CLI sub-command: init
    init_parser = subparsers.add_parser("init", help="Create a starter YAML model")
    init_parser.add_argument("--template", choices=["min", "full"], default="min")
    init_parser.add_argument("--output", default="cost_of_running.yaml")
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=cmd_init)

    # CLI sub-command: validate
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

    # CLI sub-command: measure
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
    """
    Main entry point for the NextEco CLI application.

    Returns
    -------
    int
        Exit code representing the execution result of the invoked sub-command.
    """
    # Orchestrate the routing of command line arguments manually
    parser = build_parser()
    args = parser.parse_args()
    
    # Each sub-command configures `args.func` allowing simple delegation
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
