"""
Data Model and Validation Layer.

This module is responsible for loading, validating, and converting
NextEco YAML cost models into standardized outputs such as human-readable
Markdown reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any
import math
import yaml


ALLOWED_STATUSES = {"measured", "estimated", "placeholder", "TODO"}


@dataclass
class ValidationIssue:
    """
    Represents a discrete validation issue found within the cost model.

    Attributes
    ----------
    level : str
        Severity of the issue, standardly "error" or "warning".
    message : str
        Human-readable description of the constraint violation.
    """
    level: str
    message: str


@dataclass
class ValidationResult:
    """
    Aggregator for issues found during a full validation pass.

    Attributes
    ----------
    issues : list[ValidationIssue]
        The collection of accumulated warnings and errors.
    """
    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, level: str, message: str) -> None:
        """
        Append a new issue to the validation result.

        Parameters
        ----------
        level : str
            Severity level, e.g., "error" or "warning".
        message : str
            Descriptor string representing what rule was violated.
        """
        self.issues.append(ValidationIssue(level=level, message=message))

    @property
    def errors(self) -> list[ValidationIssue]:
        """list[ValidationIssue]: Filter and return only the hard errors."""
        return [issue for issue in self.issues if issue.level == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """list[ValidationIssue]: Filter and return only advisory warnings."""
        return [issue for issue in self.issues if issue.level == "warning"]

    def is_valid(self) -> bool:
        """
        Check if the model passed validation.

        Returns
        -------
        bool
            True if no errors are present, otherwise False.
        """
        return not self.errors


def load_yaml(path: str | Path) -> dict[str, Any]:
    """
    Safely load a YAML file from disk into a Python dictionary.

    Parameters
    ----------
    path : str or pathlib.Path
        The filesystem path targeting the YAML manifest to be read.

    Returns
    -------
    dict[str, Any]
        The parsed YAML dictionary.

    Raises
    ------
    ValueError
        If the primary top-level node in the YAML file is not a dictionary mapping.
    """
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Top-level YAML must be a mapping.")
    return data


def write_text(path: str | Path, content: str) -> None:
    """
    Write a UTF-8 string to a specified file.

    Parameters
    ----------
    path : str or pathlib.Path
        The target location to output the content to.
    content : str
        The raw text data to be laid down on disk.
    """
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def _is_number(value: Any) -> bool:
    """
    Determine if a given value is securely treated as a numeric scalar.

    Parameters
    ----------
    value : Any
        The parsed Python object to inspect.

    Returns
    -------
    bool
        True if the value is an int or float, but strictly not a boolean.
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _status_of(obj: Any) -> str | None:
    """
    Extract the 'status' property carefully from an arbitrary mapping.

    Parameters
    ----------
    obj : Any
        The parsed dictionary item which may contain a 'status'.

    Returns
    -------
    str | None
        The status string if present, else None.
    """
    if isinstance(obj, dict):
        status = obj.get("status")
        if status is None:
            return None
        return str(status)
    return None


def _value_of(obj: Any) -> Any:
    """
    Extract the core 'value' scalar from an abstraction dictionary if necessary.

    Parameters
    ----------
    obj : Any
        The parsed dictionary wrapper containing a 'value', or the raw value itself.

    Returns
    -------
    Any
        The unwrapped intrinsic value.
    """
    if isinstance(obj, dict) and "value" in obj:
        return obj.get("value")
    return obj


def _stringify(value: Any) -> str:
    """
    Coerce a parsed object into a clean Markdown-friendly string representation.

    Parameters
    ----------
    value : Any
        The internal value to be converted.

    Returns
    -------
    str
        The formatted string representing the value, defaulting to '—' if empty.
    """
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "—"
    return str(value)


def _format_value_status(obj: Any, *, fallback_unit: str | None = None) -> str:
    """
    Intelligently format a value string combining its quantity, unit, and verification status.

    Parameters
    ----------
    obj : Any
        The container bearing 'value', 'status', and potentially 'unit'.
    fallback_unit : str, optional
        Backup unit string to append if the object does not specify one natively.

    Returns
    -------
    str
        A concatenated display string, e.g., '140.5 W (measured)'.
    """
    value = _value_of(obj)
    status = _status_of(obj)
    unit = obj.get("unit") if isinstance(obj, dict) else fallback_unit
    text = _stringify(value)
    if unit and text != "—":
        text = f"{text} {unit}"
    if status:
        text = f"{text} ({status})"
    return text


def _escape_md(value: Any) -> str:
    """
    Escape special reserved characters to render safely inside Markdown tables.

    Parameters
    ----------
    value : Any
        The raw object to be stringified and escaped.

    Returns
    -------
    str
        The robustly escaped string.
    """
    return _stringify(value).replace("|", "\\|")


def _check_status(result: ValidationResult, obj: Any, label: str) -> None:
    """
    Verify that an object possesses a strictly allowed verification status.

    Parameters
    ----------
    result : ValidationResult
        The context accumulator recording any found issues.
    obj : Any
        The dictionary container ostensibly holding a 'status'.
    label : str
        A breadcrumb key path to accurately log the location of the error.
    """
    status = _status_of(obj)
    if status is None:
        result.add("warning", f"{label} is missing a status field.")
        return
    if status not in ALLOWED_STATUSES:
        result.add("error", f"{label} has invalid status '{status}'.")


def _check_date_string(value: str) -> bool:
    """
    Confirm that a string accurately adheres to the `YYYY-MM-DD` date format.

    Parameters
    ----------
    value : str
        The raw calendar string to evaluate.

    Returns
    -------
    bool
        True if the string can be parsed into a real calendar date, else False.
    """
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except Exception:
        return False


def _days_since(date_str: str) -> int | None:
    """
    Calculate the age in days between today and a supplied historical date string.

    Parameters
    ----------
    date_str : str
        The `YYYY-MM-DD` date string representing the benchmark date.

    Returns
    -------
    int | None
        The discrete number of days elapsed, or None if the date string is malformed.
    """
    if not _check_date_string(date_str):
        return None
    then = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (date.today() - then).days


def validate_cost_model(data: dict[str, Any]) -> ValidationResult:
    """
    Perform a complete semantic validation analysis on a parsed NextEco model.

    Parameters
    ----------
    data : dict[str, Any]
        The loaded YAML abstraction representing the cost of running footprint.

    Returns
    -------
    ValidationResult
        A container aggregating any errors and warnings found during inspection.
    """
    result = ValidationResult()

    # Verify that all mandatory top-level container fields exist
    for field_name in ["date_updated", "canonical_unit_of_work", "deployment"]:
        if field_name not in data:
            result.add("error", f"Missing required top-level field: {field_name}")

    if "date_updated" in data:
        date_updated = str(data.get("date_updated"))
        if date_updated == "YYYY-MM-DD":
            result.add("warning", "date_updated is still a template placeholder.")
        elif not _check_date_string(date_updated):
            result.add("error", "date_updated must be YYYY-MM-DD")

    cuow = data.get("canonical_unit_of_work", {})
    if isinstance(cuow, dict):
        if not cuow.get("name"):
            result.add("error", "canonical_unit_of_work.name is required")
        _check_status(result, cuow, "canonical_unit_of_work")
    else:
        result.add("error", "canonical_unit_of_work must be a mapping")

    assumptions = data.get("assumptions", {})
    if assumptions and isinstance(assumptions, dict):
        for key, value in assumptions.items():
            if isinstance(value, dict) and ("value" in value or "status" in value):
                _check_status(result, value, f"assumptions.{key}")
                retrieved_date = value.get("retrieved_date")
                source_url = value.get("source_url")
                if retrieved_date is not None:
                    retrieved_date_str = str(retrieved_date)
                    if retrieved_date_str == "YYYY-MM-DD":
                        result.add(
                            "warning",
                            f"assumptions.{key}.retrieved_date is still a template placeholder.",
                        )
                    elif not _check_date_string(retrieved_date_str):
                        result.add(
                            "error",
                            f"assumptions.{key}.retrieved_date must be YYYY-MM-DD",
                        )
                    else:
                        age = _days_since(retrieved_date_str)
                        if age is not None and age > 90:
                            result.add(
                                "warning",
                                f"assumptions.{key} pricing/provenance data is older than 90 days; verify freshness.",
                            )
                if source_url is not None and source_url == "TODO":
                    result.add(
                        "warning",
                        f"assumptions.{key}.source_url still needs human verification.",
                    )

    pricing = data.get("pricing", {})
    if pricing and isinstance(pricing, dict):
        external_apis = pricing.get("external_apis", [])
        if not isinstance(external_apis, list):
            result.add("error", "pricing.external_apis must be a list")
        else:
            for idx, api in enumerate(external_apis):
                if not isinstance(api, dict):
                    result.add(
                        "error", f"pricing.external_apis[{idx}] must be a mapping"
                    )
                    continue
                price_per_unit = api.get("price_per_unit", {})
                usage_per_unit = api.get("usage_per_canonical_unit", {})
                subtotal = api.get("subtotal_usd", {})
                _check_status(
                    result,
                    price_per_unit,
                    f"pricing.external_apis[{idx}].price_per_unit",
                )
                _check_status(
                    result,
                    usage_per_unit,
                    f"pricing.external_apis[{idx}].usage_per_canonical_unit",
                )
                _check_status(
                    result, subtotal, f"pricing.external_apis[{idx}].subtotal_usd"
                )
                source_url = price_per_unit.get("source_url")
                retrieved_date = price_per_unit.get("retrieved_date")
                if source_url in (None, "", "TODO"):
                    result.add(
                        "warning",
                        f"pricing.external_apis[{idx}].price_per_unit.source_url should be set.",
                    )
                if retrieved_date:
                    retrieved_date_str = str(retrieved_date)
                    if retrieved_date_str == "YYYY-MM-DD":
                        result.add(
                            "warning",
                            f"pricing.external_apis[{idx}].price_per_unit.retrieved_date is still a template placeholder.",
                        )
                    elif not _check_date_string(retrieved_date_str):
                        result.add(
                            "error",
                            f"pricing.external_apis[{idx}].price_per_unit.retrieved_date must be YYYY-MM-DD",
                        )
                    else:
                        age = _days_since(retrieved_date_str)
                        if age is not None and age > 90:
                            result.add(
                                "warning",
                                f"pricing.external_apis[{idx}] pricing metadata is older than 90 days; verify freshness.",
                            )

                price_value = _value_of(price_per_unit)
                usage_value = _value_of(usage_per_unit)
                subtotal_value = _value_of(subtotal)
                if (
                    _is_number(price_value)
                    and _is_number(usage_value)
                    and _is_number(subtotal_value)
                ):
                    expected = float(price_value) * float(usage_value)
                    if not math.isclose(
                        float(subtotal_value), expected, rel_tol=1e-9, abs_tol=1e-9
                    ):
                        result.add(
                            "error",
                            f"pricing.external_apis[{idx}].subtotal_usd does not match price_per_unit × usage_per_canonical_unit",
                        )

    scenarios = []
    if "scenario" in data:
        scenarios = [data["scenario"]]
    elif "scenarios" in data:
        scenarios = data["scenarios"]

    if not scenarios:
        result.add("error", "A model must define either 'scenario' or 'scenarios'.")
    if not isinstance(scenarios, list):
        result.add(
            "error", "Scenarios must be represented as a list after normalization."
        )
        return result

    for idx, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            result.add("error", f"scenario[{idx}] must be a mapping")
            continue

        if not scenario.get("name"):
            result.add("warning", f"scenario[{idx}] should have a name")

        runtime = scenario.get("runtime_seconds", {})
        _check_status(result, runtime, f"scenario[{idx}].runtime_seconds")

        local_compute = scenario.get("local_compute", {})
        if isinstance(local_compute, dict):
            energy = local_compute.get("energy_kwh", {})
            elec_cost = local_compute.get("electricity_cost_usd", {})
            carbon = local_compute.get("carbon_gco2e", {})
            _check_status(result, energy, f"scenario[{idx}].local_compute.energy_kwh")
            _check_status(
                result, elec_cost, f"scenario[{idx}].local_compute.electricity_cost_usd"
            )
            _check_status(result, carbon, f"scenario[{idx}].local_compute.carbon_gco2e")

        external_api_cost = scenario.get("external_api_cost_usd", {})
        _check_status(
            result, external_api_cost, f"scenario[{idx}].external_api_cost_usd"
        )

        totals = scenario.get("totals", {})
        if isinstance(totals, dict):
            total_cost = totals.get("total_cost_usd", {})
            total_carbon = totals.get("total_carbon_gco2e", {})
            _check_status(result, total_cost, f"scenario[{idx}].totals.total_cost_usd")
            _check_status(
                result, total_carbon, f"scenario[{idx}].totals.total_carbon_gco2e"
            )

            local_cost_value = (
                _value_of(local_compute.get("electricity_cost_usd", {}))
                if isinstance(local_compute, dict)
                else None
            )
            api_cost_value = _value_of(external_api_cost)
            total_cost_value = _value_of(total_cost)
            if (
                _is_number(local_cost_value)
                and _is_number(api_cost_value)
                and _is_number(total_cost_value)
            ):
                expected = float(local_cost_value) + float(api_cost_value)
                if not math.isclose(
                    float(total_cost_value), expected, rel_tol=1e-9, abs_tol=1e-9
                ):
                    result.add(
                        "error",
                        f"scenario[{idx}].totals.total_cost_usd does not equal local + external API cost",
                    )

            local_carbon_value = (
                _value_of(local_compute.get("carbon_gco2e", {}))
                if isinstance(local_compute, dict)
                else None
            )
            total_carbon_value = _value_of(total_carbon)
            if _is_number(local_carbon_value) and _is_number(total_carbon_value):
                if float(total_carbon_value) < float(local_carbon_value):
                    result.add(
                        "error",
                        f"scenario[{idx}].totals.total_carbon_gco2e cannot be smaller than local carbon",
                    )

    return result


def normalize_scenarios(data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract and normalize the scenario list uniformly, regardless of singular/plural keys.

    Parameters
    ----------
    data : dict[str, Any]
        The root document which may contain a 'scenario' object or a 'scenarios' list.

    Returns
    -------
    list[dict[str, Any]]
        A list of mapped scenarios, empty if none are correctly formatted.
    """
    if "scenarios" in data and isinstance(data["scenarios"], list):
        return data["scenarios"]
    if "scenario" in data and isinstance(data["scenario"], dict):
        return [data["scenario"]]
    return []


def _append_kv_section(lines: list[str], title: str, mapping: dict[str, Any]) -> None:
    if not mapping:
        return
    lines.append(f"## {title}")
    lines.append("")
    for key, value in mapping.items():
        lines.append(f"- **{key.replace('_', ' ')}**: {_stringify(value)}")
    lines.append("")


def _append_structured_mapping(
    lines: list[str], title: str, mapping: dict[str, Any]
) -> None:
    if not mapping:
        return
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for key, value in mapping.items():
        if isinstance(value, dict) and ("value" in value or "status" in value):
            lines.append(f"| {key} | {_escape_md(_format_value_status(value))} |")
        else:
            lines.append(f"| {key} | {_escape_md(value)} |")
    lines.append("")


def render_markdown(data: dict[str, Any]) -> str:
    """
    Compile a validated NextEco YAML model into a rich Markdown report.

    Parameters
    ----------
    data : dict[str, Any]
        The parsed source model, ideally having already passed `validate_cost_model`.

    Returns
    -------
    str
        The fully stitched Markdown document string ready to be written to disk.
    """
    scenarios = normalize_scenarios(data)
    lines: list[str] = []
    lines.append("# Cost of Running")
    lines.append("")
    lines.append(f"- Date updated: `{data.get('date_updated', 'unknown')}`")
    lines.append("")

    cuow = data.get("canonical_unit_of_work", {})
    lines.append("## Canonical unit of work")
    lines.append("")
    lines.append(f"- Name: **{cuow.get('name', 'unknown')}**")
    if cuow.get("description"):
        lines.append(f"- Description: {cuow.get('description')}")
    if cuow.get("status"):
        lines.append(f"- Status: `{cuow.get('status')}`")
    notes = cuow.get("notes")
    if notes:
        lines.append(f"- Notes: {notes}")
    out_of_scope = cuow.get("out_of_scope", [])
    if out_of_scope:
        lines.append("- Out of scope:")
        for item in out_of_scope:
            lines.append(f"  - {item}")
    lines.append("")

    _append_kv_section(lines, "Deployment context", data.get("deployment", {}))

    assumptions = data.get("assumptions", {})
    if assumptions:
        lines.append("## Assumptions")
        lines.append("")
        for key, value in assumptions.items():
            lines.append(f"### {key}")
            lines.append("")
            if isinstance(value, dict):
                lines.append("| Field | Value |")
                lines.append("|---|---|")
                for subkey, subvalue in value.items():
                    lines.append(f"| {subkey} | {_escape_md(subvalue)} |")
            else:
                lines.append(f"- Value: {_stringify(value)}")
            lines.append("")

    pricing = data.get("pricing", {})
    external_apis = (
        pricing.get("external_apis", []) if isinstance(pricing, dict) else []
    )
    if external_apis:
        lines.append("## External API pricing")
        lines.append("")
        for api in external_apis:
            lines.append(f"### {api.get('name', 'unknown-api')}")
            lines.append("")
            lines.append("| Metric | Value | Status | Notes |")
            lines.append("|---|---:|---|---|")
            price = api.get("price_per_unit", {})
            usage = api.get("usage_per_canonical_unit", {})
            subtotal = api.get("subtotal_usd", {})
            lines.append(
                f"| Price per unit | {_escape_md(_stringify(_value_of(price)))} | {_escape_md(_status_of(price) or '—')} | {_escape_md(price.get('unit') if isinstance(price, dict) else '—')} |"
            )
            lines.append(
                f"| Usage per canonical unit | {_escape_md(_stringify(_value_of(usage)))} | {_escape_md(_status_of(usage) or '—')} | {_escape_md(usage.get('unit') if isinstance(usage, dict) else '—')} |"
            )
            price_note = []
            if isinstance(price, dict):
                if price.get("source_url"):
                    price_note.append(f"source: {price.get('source_url')}")
                if price.get("retrieved_date"):
                    price_note.append(f"retrieved: {price.get('retrieved_date')}")
            lines.append(
                f"| Subtotal USD | {_escape_md(_stringify(_value_of(subtotal)))} | {_escape_md(_status_of(subtotal) or '—')} | {_escape_md('; '.join(price_note) if price_note else '—')} |"
            )
            lines.append("")

    lines.append("## Scenarios")
    lines.append("")
    for scenario in scenarios:
        lines.append(f"### {scenario.get('name', 'unnamed')}")
        lines.append("")
        if scenario.get("description"):
            lines.append(scenario.get("description"))
            lines.append("")
        runtime = scenario.get("runtime_seconds", {})
        local_compute = scenario.get("local_compute", {})
        totals = scenario.get("totals", {})
        lines.append("| Metric | Value | Status | Notes |")
        lines.append("|---|---:|---|---|")
        lines.append(
            f"| Runtime seconds | {_escape_md(_stringify(_value_of(runtime)))} | {_escape_md(_status_of(runtime) or '—')} | {_escape_md(runtime.get('notes') if isinstance(runtime, dict) else '—')} |"
        )
        lines.append(
            f"| Energy kWh | {_escape_md(_stringify(_value_of(local_compute.get('energy_kwh', {}))))} | {_escape_md(_status_of(local_compute.get('energy_kwh', {})) or '—')} | {_escape_md(local_compute.get('energy_kwh', {}).get('notes') if isinstance(local_compute.get('energy_kwh', {}), dict) else '—')} |"
        )
        lines.append(
            f"| Electricity cost USD | {_escape_md(_stringify(_value_of(local_compute.get('electricity_cost_usd', {}))))} | {_escape_md(_status_of(local_compute.get('electricity_cost_usd', {})) or '—')} | {_escape_md(local_compute.get('electricity_cost_usd', {}).get('notes') if isinstance(local_compute.get('electricity_cost_usd', {}), dict) else '—')} |"
        )
        lines.append(
            f"| Carbon gCO2e | {_escape_md(_stringify(_value_of(local_compute.get('carbon_gco2e', {}))))} | {_escape_md(_status_of(local_compute.get('carbon_gco2e', {})) or '—')} | {_escape_md(local_compute.get('carbon_gco2e', {}).get('notes') if isinstance(local_compute.get('carbon_gco2e', {}), dict) else '—')} |"
        )
        external_api_cost = scenario.get("external_api_cost_usd", {})
        lines.append(
            f"| External API cost USD | {_escape_md(_stringify(_value_of(external_api_cost)))} | {_escape_md(_status_of(external_api_cost) or '—')} | {_escape_md(external_api_cost.get('notes') if isinstance(external_api_cost, dict) else '—')} |"
        )
        lines.append(
            f"| Total cost USD | {_escape_md(_stringify(_value_of(totals.get('total_cost_usd', {}))))} | {_escape_md(_status_of(totals.get('total_cost_usd', {})) or '—')} | {_escape_md(totals.get('total_cost_usd', {}).get('notes') if isinstance(totals.get('total_cost_usd', {}), dict) else '—')} |"
        )
        lines.append(
            f"| Total carbon gCO2e | {_escape_md(_stringify(_value_of(totals.get('total_carbon_gco2e', {}))))} | {_escape_md(_status_of(totals.get('total_carbon_gco2e', {})) or '—')} | {_escape_md(totals.get('total_carbon_gco2e', {}).get('notes') if isinstance(totals.get('total_carbon_gco2e', {}), dict) else '—')} |"
        )
        lines.append("")

    exclusions = data.get("exclusions", [])
    if exclusions:
        lines.append("## Exclusions")
        lines.append("")
        for item in exclusions:
            lines.append(f"- {item}")
        lines.append("")

    output_expectations = data.get("output_expectations", {})
    if output_expectations:
        _append_structured_mapping(lines, "Output expectations", output_expectations)

    lines.append("## Notes")
    lines.append("")
    lines.append("- Generated by NextEco.")
    lines.append("- The YAML file remains the source of truth.")
    lines.append("- Re-run `nexteco validate` and `nexteco render` after edits.")
    lines.append("")
    return "\n".join(lines)
