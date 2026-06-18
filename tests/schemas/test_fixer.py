"""Tests for the Fixer output schema."""

import pytest
from pydantic import ValidationError

from patchbench.schemas import FixerOutput, FixerType


def _valid_fixer_dict():
    # Mirrors the example in the design doc (Schema 3).
    return {
        "bug_id": "BUG_001",
        "fixer_type": "LogicFixer",
        "files_modified": ["src/cart.py"],
        "patch": "unified_diff_here",
        "confidence": 0.88,
        "root_cause": "Discount sign was reversed.",
        "explanation": "Changed subtraction logic to correctly apply discount.",
    }


def test_parses_doc_example_and_coerces_fixer_type():
    fixer = FixerOutput(**_valid_fixer_dict())
    assert fixer.fixer_type is FixerType.LOGIC_FIXER
    assert fixer.files_modified == ["src/cart.py"]
    assert fixer.confidence == 0.88


def test_rejects_unknown_fixer_type():
    data = _valid_fixer_dict()
    data["fixer_type"] = "MagicFixer"
    with pytest.raises(ValidationError):
        FixerOutput(**data)


def test_rejects_out_of_range_confidence():
    data = _valid_fixer_dict()
    data["confidence"] = 1.5
    with pytest.raises(ValidationError):
        FixerOutput(**data)


def test_round_trip_json():
    fixer = FixerOutput(**_valid_fixer_dict())
    assert FixerOutput.model_validate_json(fixer.model_dump_json()) == fixer
