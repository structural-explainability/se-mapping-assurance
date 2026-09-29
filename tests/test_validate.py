"""Test schema-derived checks and status consistency without research judgments."""

from dataclasses import asdict
from typing import Any

import pytest

from se_mapping_assurance.record import MappingRecord
from se_mapping_assurance.validate import validate_mapping


def test_open_record_passes(open_record: dict) -> None:
    assert validate_mapping(open_record).ok


def test_typed_record_passes(open_record: dict) -> None:
    record = MappingRecord.from_dict(open_record)
    assert validate_mapping(record).ok
    assert asdict(record)["record_id"] == "DEMO-001"


@pytest.mark.parametrize(
    "field_name",
    [
        "record_id",
        "status",
        "source_url",
        "reviewed_material",
        "outcome_statement",
        "analysis_completed",
        "analysis_pending",
        "related_material",
    ],
)
def test_missing_required_fields(open_record: dict, field_name: str) -> None:
    open_record.pop(field_name)
    result = validate_mapping(open_record)
    assert any(
        issue.field == field_name and issue.severity == "error"
        for issue in result.issues
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "reviewed_material",
        "evidence_source_described",
        "evidence_to_be_established",
        "evaluator_conditions",
        "applicable_concepts",
        "related_material",
    ],
)
def test_required_lists_nonempty(open_record: dict, field_name: str) -> None:
    open_record[field_name] = []
    assert not validate_mapping(open_record).ok


def test_optional_lists_absent_is_valid(open_record: dict) -> None:
    assert validate_mapping(open_record).ok


def test_required_list_items_are_strings(open_record: dict) -> None:
    open_record["reviewed_material"] = [1]
    assert any(
        issue.field == "reviewed_material"
        for issue in validate_mapping(open_record).issues
    )


def test_blank_list_entries_are_rejected(open_record: dict) -> None:
    open_record["related_material"] = ["  "]
    assert not validate_mapping(open_record).ok


def test_required_text_cannot_be_blank(open_record: dict) -> None:
    open_record["theory_boundary"] = "  "
    assert not validate_mapping(open_record).ok


@pytest.mark.parametrize("identifier", ["DEMO1", "demo-001", "D-1"])
def test_record_id_pattern(open_record: dict, identifier: str) -> None:
    open_record["record_id"] = identifier
    assert not validate_mapping(open_record).ok


def test_unrecognized_status(open_record: dict) -> None:
    open_record["status"] = "CERTIFIED"
    assert not validate_mapping(open_record).ok


def test_invalid_url(open_record: dict) -> None:
    open_record["source_url"] = "not a url"
    assert not validate_mapping(open_record).ok


def test_open_requires_pending(open_record: dict) -> None:
    open_record["analysis_pending"] = []
    result = validate_mapping(open_record)
    assert any(issue.field == "analysis_pending" for issue in result.issues)


@pytest.mark.parametrize("status", ["CLOSED_NO_FINDING", "CLOSED_FINDING"])
def test_closed_forbids_pending(open_record: dict, status: str) -> None:
    open_record["status"] = status
    assert not validate_mapping(open_record).ok
    open_record["analysis_pending"] = []
    assert validate_mapping(open_record).ok


def test_superseded_has_no_undeclared_status_rule(open_record: dict) -> None:
    open_record["status"] = "SUPERSEDED"
    open_record["analysis_pending"] = []
    assert validate_mapping(open_record).ok


def test_unknown_fields_warn_or_fail_strict(open_record: dict) -> None:
    open_record["unrecognized_field"] = "possible typo"
    regular = validate_mapping(open_record)
    assert regular.ok and any(issue.severity == "warning" for issue in regular.issues)
    assert not validate_mapping(open_record, strict=True).ok


def test_semantic_content_is_not_judged(open_record: dict) -> None:
    open_record["outcome_statement"] = (
        "A substantive conclusion requiring external review."
    )
    open_record["mapping_explanation"] = "A disputed interpretation."
    assert validate_mapping(open_record).ok


def test_non_table_record_rejected() -> None:
    assert not validate_mapping(["not a TOML table"]).ok


def test_schema_constraints_are_used(open_record: dict, schema: dict) -> None:
    altered: dict[str, Any] = {**schema, "field": {**schema["field"]}}
    altered["field"]["focus"] = {"required": False, "type": "text"}
    open_record.pop("focus")
    assert validate_mapping(open_record, schema=altered).ok
