"""CLI for structural assurance-mapping validation.

Commands:
    se-mapping-assurance validate-schema [--path PATH] [--strict]
    se-mapping-assurance validate-mapping --path PATH [--schema-path PATH] [--strict]
    se-mapping-assurance check-version [--require-tag]
"""

import argparse
from collections.abc import Callable, Sequence
from pathlib import Path
import tomllib

from se_mapping_assurance import check_version
from se_mapping_assurance.load import load_mapping, load_schema
from se_mapping_assurance.validate import ValidationResult, validate_mapping
from se_mapping_assurance.validate_schema import validate_schema

Command = Callable[[argparse.Namespace], int]
EXIT_NO_COMMAND = 2


def _report(result: ValidationResult, label: str) -> int:
    """Print field-level diagnostics and return a process exit code."""
    for issue in result.issues:
        print(f"[{issue.severity}] {issue.field}: {issue.message}")
    print(f"[{label}] {'OK' if result.ok else 'FAILED'}")
    return 0 if result.ok else 1


def _run_schema(args: argparse.Namespace) -> int:
    """Load and structurally validate an assurance schema."""
    return _report(
        validate_schema(load_schema(args.path), strict=args.strict), "schema"
    )


def _run_mapping(args: argparse.Namespace) -> int:
    """Load one mapping record and validate it without research judgments."""
    schema = load_schema(args.schema_path)
    return _report(
        validate_mapping(load_mapping(args.path), schema=schema, strict=args.strict),
        "mapping",
    )


def _run_version(args: argparse.Namespace) -> int:
    """Check release version declarations."""
    return check_version.run(require_tag=args.require_tag)


def build_parser() -> argparse.ArgumentParser:
    """Declare the supported commands and their arguments."""
    parser = argparse.ArgumentParser(
        prog="se-mapping-assurance",
        description="Validate assurance-mapping schemas and record structure.",
    )
    subparsers = parser.add_subparsers(dest="command")

    schema = subparsers.add_parser(
        "validate-schema", help="Validate the assurance schema"
    )
    schema.add_argument("--path", type=Path, help="Defaults to the canonical schema")
    schema.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    schema.set_defaults(func=_run_schema)

    mapping = subparsers.add_parser(
        "validate-mapping", help="Validate one assurance-mapping TOML file"
    )
    mapping.add_argument("--path", type=Path, required=True, help="Mapping record file")
    mapping.add_argument(
        "--schema-path", type=Path, help="Defaults to the canonical schema"
    )
    mapping.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    mapping.set_defaults(func=_run_mapping)

    version = subparsers.add_parser(
        "check-version", help="Check release version consistency"
    )
    version.add_argument(
        "--require-tag", action="store_true", help="Require a release Git tag"
    )
    version.set_defaults(func=_run_version)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch the selected command and return its exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    action: Command | None = getattr(args, "func", None)
    if action is None:
        parser.print_help()
        return EXIT_NO_COMMAND
    try:
        return action(args)
    except (
        FileNotFoundError,
        PermissionError,
        UnicodeError,
        tomllib.TOMLDecodeError,
        ValueError,
    ) as exc:
        parser.exit(1, f"se-mapping-assurance: {exc}\n")
