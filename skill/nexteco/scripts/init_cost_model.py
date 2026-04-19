#!/usr/bin/env python3
"""
NextEco Skill Init Config.

Utility script integrated within the Agent skill set to silently scaffold cost
model manifests into the target repository.
"""
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

MIN_TEMPLATE = Path(__file__).resolve().parents[1] / 'assets' / 'cost_of_running.min.yaml.example'
FULL_TEMPLATE = Path(__file__).resolve().parents[1] / 'assets' / 'cost_of_running.full.yaml.example'


def main() -> int:
    """
    Main entry point to initialize a cost model template via the skill toolchain.

    Returns
    -------
    int
        Exit code denoting success (0) or failure to initialize without force.
    """
    # Expose 'template', 'output', and 'force' overrides to the Agent.
    parser = argparse.ArgumentParser(description='Initialize a NextEco cost model file')
    parser.add_argument('--template', choices=['min', 'full'], default='min')
    parser.add_argument('--output', default='cost_of_running.yaml')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    # Select the bundled template based on user preference
    src = MIN_TEMPLATE if args.template == 'min' else FULL_TEMPLATE
    dst = Path(args.output)
    
    # Safely halt if a manifest already resides at the target path
    if dst.exists() and not args.force:
        raise SystemExit(f'Refusing to overwrite existing file: {dst}')
        
    # Copy the template over into the working repository
    dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
    logger.info(f'Wrote {dst}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
