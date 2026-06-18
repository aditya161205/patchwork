"""Tests for the Validator output schema."""

import pytest
from pydantic import ValidationError

from patchbench.schemas import CheckStatus, TestResults, ValidatorOutput


def _valid_validator_dict():
    # Mirrors the example in the design doc (Schema 4).
    return {
        "bug_id": "BUG_001",
        "validation_status": "PASS",
        "tests_before": {"passed": 18, "failed": 1},
        "tests_after": {"passed": 19, "failed": 0},
        "lint_status": "PASS",
        "static_analysis_status": "PASS",
        "validation_report": "All tests passed successfully.",
    }


def test_parses_doc_example():
    v = ValidatorOutput(**_valid_validator_dict())
    assert v.validation_status is CheckStatus.PASS
    assert isinstance(v.tests_before, TestResults)
    assert v.tests_before.failed == 1
    assert v.tests_after.failed == 0


def test_rejects_negative_test_counts():
    with pytest.raises(ValidationError):
        TestResults(passed=-1, failed=0)


def test_rejects_unknown_status():
    data = _valid_validator_dict()
    data["validation_status"] = "MAYBE"
    with pytest.raises(ValidationError):
        ValidatorOutput(**data)


def test_round_trip_json():
    v = ValidatorOutput(**_valid_validator_dict())
    assert ValidatorOutput.model_validate_json(v.model_dump_json()) == v
