#!/usr/bin/env python3
from pathlib import Path
import argparse

MIN_TEMPLATE = Path(__file__).resolve().parents[1] / 'assets' / 'cost_of_running.min.yaml.example'
FULL_TEMPLATE = Path(__file__).resolve().parents[1] / 'assets' / 'cost_of_running.full.yaml.example'


def main() -> int:
    parser = argparse.ArgumentParser(description='Initialize a NextEco cost model file')
    parser.add_argument('--template', choices=['min', 'full'], default='min')
    parser.add_argument('--output', default='cost_of_running.yaml')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    src = MIN_TEMPLATE if args.template == 'min' else FULL_TEMPLATE
    dst = Path(args.output)
    if dst.exists() and not args.force:
        raise SystemExit(f'Refusing to overwrite existing file: {dst}')
    dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
    print(f'Wrote {dst}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
