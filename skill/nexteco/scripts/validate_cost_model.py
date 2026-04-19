#!/usr/bin/env python3
"""
NextEco Skill Validation Utility.

A stripped-down, fallback validation script intended to sanity check the target
manifest natively within the AI skill sandbox.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ALLOWED = {'measured', 'estimated', 'placeholder', 'TODO'}


def load_yaml(path: Path) -> dict:
    """
    Load a raw YAML payload from the filesystem payload into a generic dictionary.

    Parameters
    ----------
    path : pathlib.Path
        The explicit path to the YAML file.

    Returns
    -------
    dict
        The parsed Python mapping representing the YAML document.

    Raises
    ------
    ValueError
        If the file content does not map to a standard dictionary.
    """
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    if not isinstance(data, dict):
        raise ValueError('Top-level YAML must be a mapping')
    return data


def main() -> int:
    """
    Execute an essential rule validation of a local YAML cost model.

    Returns
    -------
    int
        Exit code where 0 implies structural validity, and 1 captures schematic violations.
    """
    parser = argparse.ArgumentParser(description='Validate a NextEco YAML model')
    parser.add_argument('input', nargs='?', default='cost_of_running.yaml')
    args = parser.parse_args()

    # Attempt parsing the schema directly
    data = load_yaml(Path(args.input))
    errors = []
    
    # Enforce strict top level mandatory keys
    if 'canonical_unit_of_work' not in data:
        errors.append('missing canonical_unit_of_work')
    if 'deployment' not in data:
        errors.append('missing deployment')
    # Investigate deeper validation properties
    cuow = data.get('canonical_unit_of_work', {})
    if isinstance(cuow, dict):
        status = cuow.get('status')
        if status is not None and status not in ALLOWED:
            errors.append('invalid canonical_unit_of_work.status')
    if 'scenario' not in data and 'scenarios' not in data:
        errors.append('missing scenario or scenarios')

    if errors:
        for error in errors:
            logger.error(f'ERROR: {error}')
        return 1
    logger.info('Validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
