#!/usr/bin/env python3
import sys
from nexteco.model import load_yaml, validate_cost_model


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "cost_of_running.yaml"
    data = load_yaml(path)
    result = validate_cost_model(data)
    for issue in result.issues:
        prefix = "ERROR" if issue.level == "error" else "WARN"
        print(f"{prefix}: {issue.message}")
    return 0 if result.is_valid() else 1


if __name__ == "__main__":
    raise SystemExit(main())
