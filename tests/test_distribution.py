"""Inspect built wheel contents when a distribution has been built."""

from pathlib import Path
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_built_wheel_schema_matches_root() -> None:
    wheels = list((ROOT / "dist").glob("se_mapping_assurance-*.whl"))
    if not wheels:
        pytest.skip("Run uv build before distribution verification")
    assert len(wheels) == 1
    with ZipFile(wheels[0]) as archive:
        assert archive.read("se_mapping_assurance/assurance-mapping-schema.toml") == (
            ROOT / "assurance-mapping-schema.toml"
        ).read_bytes()
