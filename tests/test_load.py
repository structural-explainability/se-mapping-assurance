"""Canonical source and packaged-resource loading tests."""

from pathlib import Path
import tomllib

import pytest

from se_mapping_assurance import load as loader

ROOT = Path(__file__).resolve().parents[1]


def test_load_schema_from_explicit_path(schema: dict) -> None:
    assert schema["meta"]["schema"] == "se-mapping-assurance"
    assert "record_id" in schema["field"]


def test_root_schema_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    assert loader.repo_root_schema_path() == ROOT / loader.SCHEMA_FILENAME


def test_root_schema_discovery_from_nested_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT / "tests")
    assert loader.repo_root_schema_path() == ROOT / loader.SCHEMA_FILENAME


def test_schema_load_falls_back_to_packaged_resource(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(loader, "files", lambda package: tmp_path)
    (tmp_path / loader.SCHEMA_FILENAME).write_text(
        (ROOT / loader.SCHEMA_FILENAME).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    assert loader.load_schema()["meta"]["version"] == "0.1.0"


def test_load_mapping_from_file() -> None:
    doc = loader.load_mapping(ROOT / "examples" / "record-001.toml")
    assert doc["record_id"] == "DEMO-001"


def test_load_mapping_rejects_bad_toml(tmp_path: Path) -> None:
    invalid = tmp_path / "bad.toml"
    invalid.write_text('record_id = "unterminated', encoding="utf-8")
    with pytest.raises(tomllib.TOMLDecodeError):
        loader.load_mapping(invalid)
