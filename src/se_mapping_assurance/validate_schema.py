"""Structural self-validation of the canonical assurance mapping schema."""

from collections.abc import Mapping
import re
from typing import Any

from se_mapping_assurance.validate import ValidationIssue, ValidationResult

_ALLOWED_FIELD_KEYS = {
    "required",
    "type",
    "description",
    "pattern",
    "values",
    "format",
    "list",
    "min_items",
}
_ALLOWED_META_KEYS = {
    "assurance_mapping_schema_id",
    "purpose",
    "schema",
    "status",
    "title",
    "version",
}
_ALLOWED_TYPES = {"string", "text", "enum"}


def validate_schema(
    schema: Mapping[str, Any], *, strict: bool = False
) -> ValidationResult:
    """Check the declarative schema without interpreting research content."""
    issues: list[ValidationIssue] = []

    def error(location: str, message: str) -> None:
        issues.append(ValidationIssue(location, message, "error"))

    def extra(location: str, message: str) -> None:
        issues.append(
            ValidationIssue(location, message, "error" if strict else "warning")
        )

    for key in sorted(schema.keys() - {"meta", "field", "validation"}):
        extra(key, "unknown top-level schema section")

    meta = schema.get("meta")
    if not isinstance(meta, dict):
        error("meta", "required TOML table is missing")
    else:
        if meta.get("schema") != "se-mapping-assurance":
            error("meta.schema", "must identify se-mapping-assurance")
        if not isinstance(meta.get("version"), str) or not meta["version"].strip():
            error("meta.version", "a non-empty schema version is required")
        for key in meta.keys() - _ALLOWED_META_KEYS:
            extra(f"meta.{key}", "unknown schema metadata field")

    fields = schema.get("field")
    if not isinstance(fields, dict) or not fields:
        error("field", "at least one field definition is required")
    else:
        for name, definition in fields.items():
            location = f"field.{name}"
            if not isinstance(definition, dict):
                error(location, "must be a TOML table")
                continue
            if not isinstance(definition.get("required"), bool):
                error(f"{location}.required", "must be a boolean")
            is_list = definition.get("list", False)
            if not isinstance(is_list, bool):
                error(f"{location}.list", "must be a boolean")
                continue
            type_name = definition.get("type")
            if is_list:
                if type_name is not None:
                    error(
                        f"{location}.type", "list fields must use list = true, not type"
                    )
            elif type_name not in _ALLOWED_TYPES:
                error(f"{location}.type", "must be string, text, or enum")
            if type_name == "enum":
                values = definition.get("values")
                if (
                    not isinstance(values, list)
                    or not values
                    or any(not isinstance(value, str) or not value for value in values)
                ):
                    error(f"{location}.values", "must contain non-empty strings")
                elif len(values) != len(set(values)):
                    error(f"{location}.values", "enum values must be unique")
            if "min_items" in definition:
                min_items = definition["min_items"]
                if not is_list or type(min_items) is not int or min_items < 0:
                    error(
                        f"{location}.min_items",
                        "must be a non-negative integer on a list",
                    )
            if "pattern" in definition:
                pattern = definition["pattern"]
                if not isinstance(pattern, str):
                    error(f"{location}.pattern", "must be a string")
                else:
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        error(
                            f"{location}.pattern", f"invalid regular expression: {exc}"
                        )
            if "format" in definition and definition["format"] != "url":
                error(f"{location}.format", "supported format is url")
            if "description" in definition and not isinstance(
                definition["description"], str
            ):
                error(f"{location}.description", "must be text")
            for key in definition.keys() - _ALLOWED_FIELD_KEYS:
                extra(f"{location}.{key}", "unknown schema field property")

    validation = schema.get("validation", {})
    if not isinstance(validation, dict):
        error("validation", "must be a TOML table")
    else:
        for name in validation.keys() - {"status"}:
            extra(f"validation.{name}", "unknown validation section")
        status_rules = validation.get("status", {})
        if not isinstance(status_rules, dict):
            error("validation.status", "must be a TOML table")
        else:
            for key, value in status_rules.items():
                if key not in {"open_requires_pending", "closed_forbids_pending"}:
                    extra(f"validation.status.{key}", "unknown validation rule")
                elif not isinstance(value, bool):
                    error(f"validation.status.{key}", "must be a boolean")
            if (
                status_rules.get("open_requires_pending") is True
                or status_rules.get("closed_forbids_pending") is True
            ) and (
                not isinstance(fields, dict)
                or not isinstance(fields.get("status"), dict)
                or not isinstance(fields.get("analysis_pending"), dict)
            ):
                error(
                    "validation.status",
                    "requires status and analysis_pending field definitions",
                )

    return ValidationResult(record_id=None, issues=issues)
