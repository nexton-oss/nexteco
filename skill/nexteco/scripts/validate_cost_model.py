#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml

ALLOWED = {'measured', 'estimated', 'placeholder', 'TODO'}


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    if not isinstance(data, dict):
        raise ValueError('Top-level YAML must be a mapping')
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate a NextEco YAML model')
    parser.add_argument('input', nargs='?', default='cost_of_running.yaml')
    args = parser.parse_args()

    data = load_yaml(Path(args.input))
    errors = []
    if 'canonical_unit_of_work' not in data:
        errors.append('missing canonical_unit_of_work')
    if 'deployment' not in data:
        errors.append('missing deployment')
    cuow = data.get('canonical_unit_of_work', {})
    if isinstance(cuow, dict):
        status = cuow.get('status')
        if status is not None and status not in ALLOWED:
            errors.append('invalid canonical_unit_of_work.status')
    if 'scenario' not in data and 'scenarios' not in data:
        errors.append('missing scenario or scenarios')

    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        return 1
    print('Validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
