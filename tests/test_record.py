"""Ensure the typed model matches the canonical flat field set."""

from dataclasses import fields

import pytest

from se_mapping_assurance.record import MappingRecord, RecordStatus


def test_model_fields_match_schema(schema: dict) -> None:
    assert {item.name for item in fields(MappingRecord)} == set(schema["field"])


def test_typed_open_record(open_record: dict) -> None:
    record = MappingRecord.from_dict(open_record)
    assert record.status is RecordStatus.OPEN
    assert record.source_related_links == []
    assert record.source_review_pending == []


def test_invalid_typed_record_has_field_diagnostic(open_record: dict) -> None:
    open_record.pop("source_document")
    with pytest.raises(ValueError, match="source_document"):
        MappingRecord.from_dict(open_record)


def test_invalid_enum_is_rejected(open_record: dict) -> None:
    open_record["status"] = "CERTIFIED"
    with pytest.raises(ValueError, match="status"):
        MappingRecord.from_dict(open_record)


def test_explicit_optional_fields(open_record: dict) -> None:
    open_record["source_related_links"] = ["https://example.org/companion"]
    open_record["source_review_pending"] = ["Illustrative outstanding review"]
    record = MappingRecord.from_dict(open_record)
    assert len(record.source_review_pending) == 1
