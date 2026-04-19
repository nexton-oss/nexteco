from pathlib import Path

from nexteco.model import load_yaml, render_markdown, validate_cost_model


def _valid_data() -> dict:
    return {
        "date_updated": "2026-04-19",
        "canonical_unit_of_work": {
            "name": "one request",
            "status": "estimated",
        },
        "deployment": {"provider": "local"},
        "scenario": {
            "name": "default",
            "runtime_seconds": {"value": 2.0, "status": "estimated"},
            "local_compute": {
                "energy_kwh": {"value": 0.001, "status": "estimated"},
                "electricity_cost_usd": {"value": 0.2, "status": "estimated"},
                "carbon_gco2e": {"value": 0.3, "status": "estimated"},
            },
            "external_api_cost_usd": {"value": 0.4, "status": "estimated"},
            "totals": {
                "total_cost_usd": {"value": 0.6, "status": "estimated"},
                "total_carbon_gco2e": {"value": 0.3, "status": "estimated"},
            },
        },
    }


def test_min_example_is_structurally_valid():
    data = load_yaml(Path("cost_of_running.min.yaml.example"))
    result = validate_cost_model(data)
    assert result.is_valid()


def test_render_contains_expected_sections_and_table_rows():
    data = load_yaml(Path("cost_of_running.min.yaml.example"))
    markdown = render_markdown(data)
    assert "# Cost of Running" in markdown
    assert "## Canonical unit of work" in markdown
    assert "## Scenarios" in markdown
    assert "| Metric | Value | Status | Notes |" in markdown
    assert "| Total cost USD |" in markdown


def test_total_cost_arithmetic_check():
    result = validate_cost_model(_valid_data())
    assert result.is_valid()


def test_total_cost_arithmetic_failure_is_detected():
    data = _valid_data()
    data["scenario"]["totals"]["total_cost_usd"]["value"] = 0.5
    result = validate_cost_model(data)
    assert not result.is_valid()
    assert any("total_cost_usd" in issue.message for issue in result.errors)


def test_invalid_status_is_detected():
    data = _valid_data()
    data["scenario"]["runtime_seconds"]["status"] = "guess"
    result = validate_cost_model(data)
    assert not result.is_valid()
    assert any("invalid status" in issue.message for issue in result.errors)


def test_placeholder_date_updated_warns():
    data = _valid_data()
    data["date_updated"] = "YYYY-MM-DD"
    result = validate_cost_model(data)
    assert any("date_updated" in issue.message for issue in result.warnings)


def test_external_api_subtotal_mismatch_is_detected():
    data = _valid_data()
    data["pricing"] = {
        "external_apis": [
            {
                "name": "demo-api",
                "price_per_unit": {
                    "value": 2.0,
                    "unit": "USD / 1M tokens",
                    "status": "estimated",
                    "source_url": "https://example.com/pricing",
                    "retrieved_date": "2026-04-19",
                },
                "usage_per_canonical_unit": {
                    "value": 3.0,
                    "unit": "1M tokens",
                    "status": "estimated",
                },
                "subtotal_usd": {"value": 5.0, "status": "estimated"},
            }
        ]
    }
    result = validate_cost_model(data)
    assert not result.is_valid()
    assert any("subtotal_usd" in issue.message for issue in result.errors)
