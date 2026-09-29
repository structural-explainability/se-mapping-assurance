# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

## [Unreleased]

---

## [0.1.0] - 2026-09-29

### Added

- Initial assurance-mapping record schema for Structural Explainability.
- Canonical root-level `assurance-mapping-schema.toml`, included in package distributions.
- Typed assurance-mapping record representation.
- TOML record loading and structural validation.
- Validation of required fields, types, enumerated values, and list constraints.
- Status-consistency checks, including pending-analysis requirements for
  `OPEN` and `CLOSED_*` records.
- CLI commands: `validate-schema`, `validate-mapping`, and `check-version`.
- An example mapping record and automated tests.
- Documentation, repository scaffolding, and CI.
- Dependency on `se-mapspec` for general structural mapping definitions.

### Scope

Validation establishes that a record conforms to the declared structural
contract.
It does not establish the correctness of source interpretation,
the applicability of formal results, the existence of framework gaps,
or the sufficiency of assurance evidence.

Framework-specific mappings and research findings remain in consuming
repositories.

---

## Notes on versioning and releases

We use **SemVer**:

- **MAJOR** - Breaking changes to artifact structure or validation semantics.
- **MINOR** - Backward-compatible additions to schema or validation rules.
- **PATCH** - Fixes, documentation, and tooling.

Package versions are derived from Git tags. Tag `vX.Y.Z` to release.

The version in `assurance-mapping-schema.toml` tracks the schema contract
independently of the package version.
Update it when the schema contract changes.

## Release Procedure (Required)

Follow these steps exactly when creating a new release.

### Task 1. Update release metadata (manual edits)

1.1. `assurance-mapping-schema.toml` version if the schema contract changes.
1.2. CHANGELOG.md: add section, move unreleased entries, update links
1.3. `CITATION.cff` - update `version` and `date-released`
1.4. `pyproject.toml` - update build system `fallback-version`

Do not manually edit the generated `src/se_mapping_assurance/_version.py`.

### Task 2. Prepare and Validate

Run from the repository root in PowerShell.

```powershell
# Synchronize the release environment.
uv sync

# Run repository checks.
.\sit.ps1

# Update GitHub Actions and pin all action references to immutable SHAs
uvx gha-tools autoupdate --pin=all --write .github/workflows

# Update hooks
uvx prek update
git add -A
uvx prek run --all-files

# Audit the resulting GitHub configuration for security findings
uvx zizmor@latest .github/

# Validate citation metadata
uvx cffconvert --validate

# Format markdown
npx markdownlint-cli2 --fix

# Check release metadata.
uv run se-mapping-assurance check-version

# Validate the canonical schema and example.
uv run se-mapping-assurance validate-schema --strict
uv run se-mapping-assurance validate-mapping --path examples/record-001.toml --strict

# Remove old build artifacts.
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

# Build both distributions.
uv build

# Validate only Python distribution artifacts.
$artifacts = Get-ChildItem dist -File |
    Where-Object { $_.Name -match '\.(whl|tar\.gz)$' } |
    Select-Object -ExpandProperty FullName

uv run python -m twine check @artifacts

# Verify that the wheel contains the canonical schema.
uv run python -c "from pathlib import Path; from zipfile import ZipFile; wheels = list(Path('dist').glob('*.whl')); assert len(wheels) == 1, 'Expected exactly one wheel'; names = ZipFile(wheels[0]).namelist(); assert 'se_mapping_assurance/assurance-mapping-schema.toml' in names, 'Packaged schema missing'; print('Wheel schema verified')"
```

### Task 4. Commit, push, tag

```shell
git add -A
git commit -m "Prepare X.Y.Z"
git push -u origin main
```

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

## Only As Needed (delete a tag)

```shell
git tag -d vX.Z.Y
git push origin :refs/tags/vX.Z.Y
```

## Links

[Unreleased]: https://github.com/structural-explainability/se-mapping-assurance/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/structural-explainability/se-mapping-assurance/releases/tag/v0.1.0

<!-- markdownlint-enable MD024 -->
