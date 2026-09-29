"""Structural validation of assurance-mapping records."""

from se_mapping_assurance.record import MappingRecord, RecordStatus
from se_mapping_assurance.validate import ValidationIssue, ValidationResult, validate_mapping

__all__ = [
    "MappingRecord",
    "RecordStatus",
    "ValidationIssue",
    "ValidationResult",
    "validate_mapping",
]
