"""Tests for the Locator output schema."""

import pytest
from pydantic import ValidationError

from patchbench.schemas import CandidateFile, CandidateFunction, LocatorOutput


def test_parses_doc_example():
    locator = LocatorOutput(
        bug_id="BUG_001",
        candidate_files=[
            {"file": "src/cart.py", "confidence": 0.92},
            {"file": "src/order.py", "confidence": 0.41},
        ],
        candidate_functions=[{"function": "calculate_total", "confidence": 0.95}],
        reasoning="Failing test directly invokes calculate_total.",
    )
    assert isinstance(locator.candidate_files[0], CandidateFile)
    assert isinstance(locator.candidate_functions[0], CandidateFunction)
    assert locator.candidate_files[0].confidence == 0.92


def test_empty_candidate_lists_default():
    locator = LocatorOutput(bug_id="BUG_001")
    assert locator.candidate_files == []
    assert locator.candidate_functions == []
    assert locator.reasoning == ""


@pytest.mark.parametrize("bad_confidence", [-0.1, 1.1])
def test_confidence_must_be_a_probability(bad_confidence):
    with pytest.raises(ValidationError):
        CandidateFile(file="src/cart.py", confidence=bad_confidence)


def test_round_trip_json():
    locator = LocatorOutput(
        bug_id="BUG_001",
        candidate_files=[CandidateFile(file="src/cart.py", confidence=0.92)],
    )
    assert LocatorOutput.model_validate_json(locator.model_dump_json()) == locator
