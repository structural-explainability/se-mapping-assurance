"""The version checker must read metadata without changing it."""

from pathlib import Path

from se_mapping_assurance import check_version


def _write_metadata(root: Path, *, citation: str, fallback: str) -> None:
    (root / "CITATION.cff").write_text(
        f"cff-version: 1.2.0\nversion: {citation}\n", encoding="utf-8"
    )
    (root / "pyproject.toml").write_text(
        f'[tool.hatch.version]\nfallback-version = "{fallback}"\n', encoding="utf-8"
    )


def test_versions_agree(tmp_path: Path) -> None:
    _write_metadata(tmp_path, citation="0.1.0", fallback="0.1.0")
    assert check_version.run(root=tmp_path) == 0


def test_mismatching_fallback(tmp_path: Path) -> None:
    _write_metadata(tmp_path, citation="0.1.0", fallback="0.1.1")
    assert check_version.run(root=tmp_path) == 1


def test_missing_metadata(tmp_path: Path) -> None:
    assert check_version.run(root=tmp_path) == 1


def test_require_tag(
    tmp_path: Path, monkeypatch
) -> None:
    _write_metadata(tmp_path, citation="0.1.0", fallback="0.1.0")
    monkeypatch.setattr(check_version, "git_tag", lambda _: "v0.1.0")
    assert check_version.run(require_tag=True, root=tmp_path) == 0
    monkeypatch.setattr(check_version, "git_tag", lambda _: "v0.1.1")
    assert check_version.run(require_tag=True, root=tmp_path) == 1
