"""Typed representation of a single assurance-mapping record.

Field names follow the canonical assurance-mapping-schema.toml exactly.
The record model does not determine the validity of a research finding.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class RecordStatus(StrEnum):
    """Declared workflow status; not a conclusion calculated by this package."""

    OPEN = "OPEN"
    CLOSED_NO_FINDING = "CLOSED_NO_FINDING"
    CLOSED_FINDING = "CLOSED_FINDING"
    SUPERSEDED = "SUPERSEDED"


@dataclass(frozen=True, kw_only=True, slots=True)
class MappingRecord:
    """One validated, flat TOML mapping record."""

    record_id: str
    status: RecordStatus
    framework: str
    focus: str
    source_publisher: str
    source_document: str
    source_version_or_date: str
    source_url: str
    reviewed_material: list[str]
    source_structure: str
    evaluative_claim: str
    claim_adoption_status: str
    required_distinctions: str
    evidence_source_described: list[str]
    evidence_to_be_established: list[str]
    evaluator_conditions: list[str]
    assumptions: str
    applicable_concepts: list[str]
    mapping_explanation: str
    theory_boundary: str
    research_question: str
    analysis_completed: list[str]
    analysis_pending: list[str]
    counterexample_caveat: str
    outcome_statement: str
    possible_outcomes: str
    related_material: list[str]
    source_related_links: list[str] = field(default_factory=list)
    source_review_pending: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MappingRecord":
        """Build a typed record after schema validation, with field diagnostics."""
        from se_mapping_assurance.validate import validate_mapping

        result = validate_mapping(data, strict=True)
        if not result.ok:
            details = "; ".join(
                f"{issue.field}: {issue.message}"
                for issue in result.issues
                if issue.severity == "error"
            )
            raise ValueError(f"Invalid assurance-mapping record: {details}")
        values = dict(data)
        values["status"] = RecordStatus(values["status"])
        values.setdefault("source_related_links", [])
        values.setdefault("source_review_pending", [])
        return cls(**values)
