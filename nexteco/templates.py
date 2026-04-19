from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent

MIN_TEMPLATE_PATH = REPO_ROOT / "cost_of_running.min.yaml.example"
FULL_TEMPLATE_PATH = REPO_ROOT / "cost_of_running.full.yaml.example"


def get_template_text(template_name: str) -> str:
    mapping = {
        "min": MIN_TEMPLATE_PATH,
        "full": FULL_TEMPLATE_PATH,
    }
    try:
        path = mapping[template_name]
    except KeyError as exc:
        raise ValueError(f"Unknown template: {template_name}") from exc
    return path.read_text(encoding="utf-8")
