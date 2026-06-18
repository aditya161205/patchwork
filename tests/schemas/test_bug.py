"""Tests for the Bug schema."""

import pytest
from pydantic import ValidationError

from patchbench.schemas import Bug, BugType, Difficulty


def _valid_bug_dict():
    # Mirrors the example in the design doc (Schema 1).
    return {
        "bug_id": "BUG_001",
        "title": "Incorrect cart total calculation",
        "bug_type": "logical_error",
        "difficulty": "medium",
        "repo_path": "repos/cart_app",
        "issue_description": "Cart total is incorrect when discount is applied.",
        "stack_trace": "...",
        "failing_tests": ["test_discount_calculation"],
        "expected_behavior": "Discount should reduce total.",
        "actual_behavior": "Discount increases total.",
    }


def test_parses_doc_example_and_coerces_enums():
    bug = Bug(**_valid_bug_dict())
    assert bug.bug_id == "BUG_001"
    assert bug.bug_type is BugType.LOGICAL_ERROR
    assert bug.difficulty is Difficulty.MEDIUM
    assert bug.failing_tests == ["test_discount_calculation"]


def test_stack_trace_optional_and_failing_tests_default_empty():
    data = _valid_bug_dict()
    del data["stack_trace"]
    del data["failing_tests"]
    bug = Bug(**data)
    assert bug.stack_trace is None
    assert bug.failing_tests == []


def test_round_trip_json():
    bug = Bug(**_valid_bug_dict())
    assert Bug.model_validate_json(bug.model_dump_json()) == bug


def test_rejects_unknown_bug_type():
    data = _valid_bug_dict()
    data["bug_type"] = "not_a_real_type"
    with pytest.raises(ValidationError):
        Bug(**data)


def test_rejects_empty_bug_id():
    data = _valid_bug_dict()
    data["bug_id"] = ""
    with pytest.raises(ValidationError):
        Bug(**data)
