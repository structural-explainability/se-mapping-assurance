"""Load mapping records and the canonical packaged assurance schema."""

from importlib.resources import files
from pathlib import Path
import tomllib
from typing import Any, Final

SCHEMA_FILENAME: Final[str] = "assurance-mapping-schema.toml"
PACKAGE_NAME: Final[str] = "se_mapping_assurance"


def load_toml(path: Path) -> dict[str, Any]:
    """Read a TOML document, preserving parse errors for the caller."""
    with path.open("rb") as stream:
        return tomllib.load(stream)


def repo_root_schema_path(start: Path | None = None) -> Path | None:
    """Find this repository's root schema, if executing in its source tree."""
    current = (start or Path.cwd()).resolve()
    for root in (current, *current.parents):
        pyproject = root / "pyproject.toml"
        schema = root / SCHEMA_FILENAME
        source_package = root / "src" / PACKAGE_NAME
        if not (pyproject.is_file() and schema.is_file() and source_package.is_dir()):
            continue
        try:
            metadata = load_toml(pyproject)
        except (OSError, tomllib.TOMLDecodeError):
            continue
        if metadata.get("project", {}).get("name") == "se-mapping-assurance":
            return schema
    return None


def schema_text(path: Path | None = None) -> str:
    """Read an explicit schema, source-root schema, or installed resource."""
    if path is not None:
        return path.read_text(encoding="utf-8-sig")
    if root_schema := repo_root_schema_path():
        return root_schema.read_text(encoding="utf-8-sig")
    resource = files(PACKAGE_NAME).joinpath(SCHEMA_FILENAME)
    return resource.read_text(encoding="utf-8-sig")


def load_schema(path: Path | None = None) -> dict[str, Any]:
    """Parse an assurance schema from the selected source."""
    return tomllib.loads(schema_text(path))


def load_mapping(path: Path) -> dict[str, Any]:
    """Parse one flat assurance-mapping record from a TOML file."""
    return load_toml(path)
