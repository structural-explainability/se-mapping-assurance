"""Check the declarative schema rather than a duplicate hard-coded contract."""

from copy import deepcopy

from se_mapping_assurance.validate_schema import validate_schema


def test_canonical_schema_passes_strict(schema: dict) -> None:
    assert validate_schema(schema, strict=True).ok


def test_schema_requires_meta(schema: dict) -> None:
    invalid = deepcopy(schema)
    invalid.pop("meta")
    assert not validate_schema(invalid).ok


def test_schema_rejects_invalid_regex(schema: dict) -> None:
    invalid = deepcopy(schema)
    invalid["field"]["record_id"]["pattern"] = "["
    assert not validate_schema(invalid).ok


def test_schema_rejects_undeclared_type(schema: dict) -> None:
    invalid = deepcopy(schema)
    invalid["field"]["framework"]["type"] = "verdict"
    assert not validate_schema(invalid).ok


def test_schema_rejects_invalid_min_items(schema: dict) -> None:
    invalid = deepcopy(schema)
    invalid["field"]["reviewed_material"]["min_items"] = -1
    assert not validate_schema(invalid).ok


def test_schema_rejects_invalid_status_rule(schema: dict) -> None:
    invalid = deepcopy(schema)
    invalid["validation"]["status"]["open_requires_pending"] = "yes"
    assert not validate_schema(invalid).ok


def test_unknown_schema_property_warning_becomes_error(schema: dict) -> None:
    invalid = deepcopy(schema)
    invalid["field"]["record_id"]["custom_rule"] = "x"
    assert validate_schema(invalid).ok
    assert not validate_schema(invalid, strict=True).ok
