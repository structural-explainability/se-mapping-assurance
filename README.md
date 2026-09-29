# Structural Explainability Mapping: Assurance

<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.x.svg)](https://zenodo.org/records/x) -->
[![PyPI](https://img.shields.io/pypi/v/se-mapping-assurance.svg)](https://pypi.org/project/se-mapping-assurance/)
[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CI Status](https://github.com/structural-explainability/se-mapping-assurance/actions/workflows/ci-python-zensical.yml/badge.svg)](https://github.com/structural-explainability/se-mapping-assurance/actions/workflows/ci-python-zensical.yml)
[![Docs](https://img.shields.io/badge/docs-Zensical-blue)](https://structural-explainability.github.io/se-mapping-assurance/)

> Assurance-mapping record schema and structural validation for the
> Structural Explainability ecosystem.

## Purpose

Domain-specific consumer of `se-mapspec`'s general mapping vocabulary,
scoped to records that map an external assurance or evaluation framework
against Structural Assurability.

For full documentation, see [`SPECIFICATION.md`](./SPECIFICATION.md).

## Included

- `assurance-mapping-schema.toml` - the canonical record schema.
- `src/se_mapping_assurance/record.py` - a typed record model.
- `src/se_mapping_assurance/validate.py` - structural and internal-
  consistency checks against that schema.

## Not Included

Framework-specific mapping records, findings, and
crosswalk content live in consuming repositories.

## Development

### Clone and Open in VS Code

```shell
git clone https://github.com/structural-explainability/se-mapping-assurance.git
cd se-mapping-assurance
code .
```

### Set Up the Project

```shell
uvx pup-clean --delete
uv self update
uv python pin 3.14
uv python install
uv lock --upgrade
uv sync
uv audit
```

## Canonical Schema

[assurance-mapping-schema.toml](assurance-mapping-schema.toml)

## Documentation

[Documentation](docs/en/index.md)

## Status

Initial development. The schema and validator require testing against
at least two independently developed framework mappings before release.

## Citation

[CITATION.cff](./CITATION.cff)

## License

[MIT](./LICENSE)

## Repository Manifest

[SE_MANIFEST.toml](./SE_MANIFEST.toml)
