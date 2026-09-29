"""Read-only agreement check for citation, Hatch-VCS fallback, and Git tag."""

from pathlib import Path
import re
import shutil
import subprocess
import tomllib

_CFF_VERSION = re.compile(
    r"""^version:\s*["']?(?P<version>[^"'\s#]+)["']?\s*(?:#.*)?$"""
)


def citation_version(path: Path) -> str:
    """Read the top-level version scalar from this repository's CITATION.cff."""
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if match := _CFF_VERSION.match(line):
            return match.group("version")
    raise ValueError("CITATION.cff has no top-level version")


def fallback_version(path: Path) -> str:
    """Read the Hatch-VCS fallback version without changing the project."""
    with path.open("rb") as stream:
        config = tomllib.load(stream)
    version = (
        config.get("tool", {})
        .get("hatch", {})
        .get("version", {})
        .get("fallback-version")
    )
    if not isinstance(version, str) or not version:
        raise ValueError("pyproject.toml has no Hatch-VCS fallback-version")
    return version


def git_tag(root: Path) -> str:
    """Return the exact Git tag at HEAD (required only for release checks)."""
    if not (git := shutil.which("git")):
        raise RuntimeError("git is not installed")
    result = subprocess.run(
        [git, "describe", "--tags", "--exact-match"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError("HEAD is not at a Git tag")
    return result.stdout.strip()


def run(*, require_tag: bool = False, root: Path | None = None) -> int:
    """Compare release version declarations; never edit them."""
    directory = root or Path.cwd()
    try:
        citation = citation_version(directory / "CITATION.cff")
        fallback = fallback_version(directory / "pyproject.toml")
        errors = []
        if citation != fallback:
            errors.append(f"CITATION.cff {citation} != fallback-version {fallback}")
        if require_tag:
            tag = git_tag(directory)
            if tag != f"v{citation}":
                errors.append(f"Git tag {tag} != v{citation}")
    except (OSError, ValueError, RuntimeError, tomllib.TOMLDecodeError) as exc:
        print(f"[check-version] ERROR: {exc}")
        return 1
    for issue in errors:
        print(f"[check-version] MISMATCH: {issue}")
    if not errors:
        print(f"[check-version] OK: version {citation}")
    return 1 if errors else 0
