# Specification: Structural Explainability - Assurance Mapping

## Purpose

Define and validate the record format used to map an external assurance
or evaluation framework against Structural Assurability.

This repository owns the mapping-record schema and its structural
validator.

## Ownership Boundary

This package validates the structure of mapping records.

Concretely: this repository may reject a record for being incomplete or
internally inconsistent.
It must never accept or reject a record on the grounds
that a framework has (or lacks) a gap,
that a theorem applies (or fails to apply) to a real system,
or that an assurance argument is (or is not) justified.
Those are research conclusions and belong in the
consuming repository's own findings,
not in this package's pass/fail output.

## Schema

The canonical schema is `assurance-mapping-schema.toml` at the repository
root.
`src/se_mapping_assurance/record.py` is a typed representation of
that schema.
`validate.py` checks a parsed record instance against it.

## What Validation Checks

- Structural: required fields present; list fields non-empty where the
  schema requires at least one item.
- Consistency: fields that constrain each other agree, for example, an
  `OPEN` record must have at least one pending analysis item; a `CLOSED_*`
  record must not.

## Out of Scope

This package has no input on:

- Whether the source material was read correctly.
- Whether the applicable formal concepts are the right ones.
- Whether a stated theory boundary is accurate.
- Whether an outcome's finding is correct.

## Relationship to se-mapspec

`se-mapspec` owns general mapping vocabulary, correspondence patterns, and
structural-consistency rules across the Structural Explainability
ecosystem.
This package is a domain-specific consumer of that
vocabulary for assurance-mapping records.
It does not redefine mapping primitives `se-mapspec` provides.
