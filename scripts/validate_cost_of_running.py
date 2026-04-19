#!/usr/bin/env python3
"""
NextEco Manual Validation Script.

Utility script that wraps the model validation functions to quickly spot-check
a YAML file from the command line without installing the main CLI.
"""
import sys
from nexteco.model import load_yaml, validate_cost_model
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Execute a quick validation of a cost model file.

    Returns
    -------
    int
        Exit code (0 for success, 1 for validation failures).
    """
    # Accept the specific path to validate via sys.argv or default
    path = sys.argv[1] if len(sys.argv) > 1 else "cost_of_running.yaml"
    
    # Load and execute semantic checks
    data = load_yaml(path)
    result = validate_cost_model(data)
    for issue in result.issues:
        if issue.level == "error":
            logger.error(f"{issue.message}")
        else:
            logger.warning(f"{issue.message}")
    return 0 if result.is_valid() else 1


if __name__ == "__main__":
    raise SystemExit(main())
