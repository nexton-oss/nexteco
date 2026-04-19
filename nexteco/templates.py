"""
Template Manager.

Provides utilities for resolving and loading bundled YAML examples to bootstrap models.
"""
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent

MIN_TEMPLATE_PATH = REPO_ROOT / "cost_of_running.min.yaml.example"
FULL_TEMPLATE_PATH = REPO_ROOT / "cost_of_running.full.yaml.example"


def get_template_text(template_name: str) -> str:
    """
    Retrieve the string contents of a predefined YAML example template.

    Parameters
    ----------
    template_name : str
        The short name of the requested template (e.g., 'min' or 'full').

    Returns
    -------
    str
        The complete UTF-8 contents of the target template file.

    Raises
    ------
    ValueError
        If the given `template_name` does not map to a recognized template.
    """
    mapping = {
        "min": MIN_TEMPLATE_PATH,
        "full": FULL_TEMPLATE_PATH,
    }
    try:
        path = mapping[template_name]
    except KeyError as exc:
        raise ValueError(f"Unknown template: {template_name}") from exc
    return path.read_text(encoding="utf-8")
