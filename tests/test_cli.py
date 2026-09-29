"""CLI dispatch, diagnostics, and exit codes."""

from pathlib import Path

import pytest

from se_mapping_assurance.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_help_without_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    assert "validate-mapping" in capsys.readouterr().out


def test_validate_schema(capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main(
            [
                "validate-schema",
                "--path",
                str(ROOT / "assurance-mapping-schema.toml"),
                "--strict",
            ]
        )
        == 0
    )
    assert "[schema] OK" in capsys.readouterr().out


def test_validate_mapping(capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main(
            [
                "validate-mapping",
                "--path",
                str(ROOT / "examples" / "record-001.toml"),
                "--strict",
            ]
        )
        == 0
    )
    assert "[mapping] OK" in capsys.readouterr().out


def test_bad_mapping_exits_with_field_diagnostic(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    file = tmp_path / "bad.toml"
    file.write_text('record_id = "DEMO-001"\n', encoding="utf-8")
    assert (
        main(
            [
                "validate-mapping",
                "--path",
                str(file),
                "--schema-path",
                str(ROOT / "assurance-mapping-schema.toml"),
            ]
        )
        == 1
    )
    assert "status" in capsys.readouterr().out


def test_missing_path_argument() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["validate-mapping"])
    assert exc.value.code == 2


def test_missing_file_exits_one(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["validate-mapping", "--path", "no-such-file.toml"])
    assert exc.value.code == 1
