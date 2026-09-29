"""Structural and internal-consistency checks for mapping records.

Validation makes no judgment about source interpretation, formal applicability,
framework deficiencies, or whether an assurance argument is justified.
"""

from dataclasses import asdict, dataclass
import re
from typing import Any, Literal, Mapping
from urllib.parse import urlsplit

from se_mapping_assurance.load import load_schema

Severity = Literal["error", "warning"]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One structural problem or advisory, identified by field path."""

    field: str
    message: str
    severity: Severity


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Structural validation result; never a research-outcome judgment."""

    record_id: str | None
    issues: list[ValidationIssue]

    @property
    def ok(self) -> bool:
        """Whether the record has no structural errors."""
        return not any(issue.severity == "error" for issue in self.issues)


def _is_url(value: str) -> bool:
    """Require an absolute URL with a scheme and network location."""
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and not any(
            char.isspace() for char in value
        )
    except ValueError:
        return False


def validate_mapping(
    data: Mapping[str, Any] | Any,
    *,
    schema: Mapping[str, Any] | None = None,
    strict: bool = False,
) -> ValidationResult:
    """Validate a flat mapping record using only declared schema constraints."""
    from se_mapping_assurance.record import MappingRecord
    from se_mapping_assurance.validate_schema import validate_schema

    if isinstance(data, MappingRecord):
        values: Mapping[str, Any] = asdict(data)
    elif isinstance(data, Mapping):
        values = data
    else:
        return ValidationResult(
            record_id=None,
            issues=[ValidationIssue("record", "must be a TOML table", "error")],
        )

    active_schema = schema if schema is not None else load_schema()
    schema_result = validate_schema(active_schema, strict=strict)
    if not schema_result.ok:
        return ValidationResult(record_id=None, issues=schema_result.issues)

    field_definitions = active_schema["field"]
    issues: list[ValidationIssue] = []
    record_id = values.get("record_id")
    result_id = record_id if isinstance(record_id, str) else None

    for name, definition in field_definitions.items():
        if name not in values:
            if definition["required"]:
                issues.append(ValidationIssue(name, "required field is missing", "error"))
            continue
        value = values[name]
        if definition.get("list", False):
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                issues.append(ValidationIssue(name, "must be a list of strings", "error"))
                continue
            minimum = definition.get("min_items", 0)
            if len(value) < minimum:
                issues.append(ValidationIssue(name, f"must contain at least {minimum} item(s)", "error"))
            if any(not item.strip() for item in value):
                issues.append(ValidationIssue(name, "list items must not be blank", "error"))
            continue
        if not isinstance(value, str) or not value.strip():
            issues.append(ValidationIssue(name, "must be a non-empty string", "error"))
            continue
        if definition.get("type") == "enum" and value not in definition["values"]:
            issues.append(ValidationIssue(name, "must be one of the declared enum values", "error"))
        if "pattern" in definition and re.fullmatch(definition["pattern"], value) is None:
            issues.append(ValidationIssue(name, "does not match the declared pattern", "error"))
        if definition.get("format") == "url" and not _is_url(value):
            issues.append(ValidationIssue(name, "must be an absolute HTTP(S) URL", "error"))

    for name in sorted(values.keys() - field_definitions.keys()):
        severity: Severity = "error" if strict else "warning"
        issues.append(ValidationIssue(name, "undeclared record field", severity))

    status = values.get("status")
    pending = values.get("analysis_pending")
    rules = active_schema.get("validation", {}).get("status", {})
    if isinstance(pending, list) and all(isinstance(item, str) for item in pending):
        if status == "OPEN" and rules.get("open_requires_pending") and not pending:
            issues.append(ValidationIssue("analysis_pending", "status OPEN requires pending analysis", "error"))
        if status in {"CLOSED_NO_FINDING", "CLOSED_FINDING"} and rules.get("closed_forbids_pending") and pending:
            issues.append(ValidationIssue("analysis_pending", "closed records must not have pending analysis", "error"))
    # SUPERSEDED has no additional rule in the current canonical schema.
    # Checking the semantic content of outcome_statement would cross the
    # specification's research/validation boundary, so is a review obligation.
    return ValidationResult(record_id=result_id, issues=issues)
