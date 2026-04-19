#!/usr/bin/env python3
"""
NextEco CLI Passthrough Script.

Convenience wrapper that simply imports and calls the main 'nexteco' application hook.
"""
from nexteco.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
