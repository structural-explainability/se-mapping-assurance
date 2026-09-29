"""Synthetic structural fixtures; not assertions about real assurance frameworks."""

from pathlib import Path
from typing import Any

import pytest

from se_mapping_assurance.load import load_schema

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def schema() -> dict[str, Any]:
    """Load the canonical root schema explicitly."""
    return load_schema(ROOT / "assurance-mapping-schema.toml")


@pytest.fixture
def open_record() -> dict[str, Any]:
    """A fictional OPEN record containing every required schema field."""
    return {
        "record_id": "DEMO-001",
        "status": "OPEN",
        "framework": "Illustrative framework",
        "focus": "Structural conformance example",
        "source_publisher": "Example publisher",
        "source_document": "Illustrative document",
        "source_version_or_date": "1.0",
        "source_url": "https://example.org/example",
        "reviewed_material": ["Illustrative section"],
        "source_structure": "Source-defined illustrative structure.",
        "evaluative_claim": "Illustrative claim, not an empirical assertion.",
        "claim_adoption_status": "No real system claim is adopted.",
        "required_distinctions": "Identify the alternatives specified by the source.",
        "evidence_source_described": ["Illustrative evidence category"],
        "evidence_to_be_established": ["Whether the example is internally complete"],
        "evaluator_conditions": ["Illustrative access conditions"],
        "assumptions": "Assumptions not independently verified.",
        "applicable_concepts": ["Illustrative concept reference"],
        "mapping_explanation": "Illustrative structural correspondence.",
        "theory_boundary": "No claim about an operational system is established.",
        "research_question": "Illustrative question for schema testing.",
        "analysis_completed": [],
        "analysis_pending": ["Complete illustrative analysis"],
        "counterexample_caveat": "A hypothetical counterexample proves no real-world failure.",
        "outcome_statement": "No framework deficiency or failure has been established.",
        "possible_outcomes": "Illustrative set of possible findings.",
        "related_material": ["https://example.org/related"],
    }
