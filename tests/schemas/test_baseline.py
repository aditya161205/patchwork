"""Tests for the Single-Agent Baseline output schema."""

import pytest
from pydantic import ValidationError

from patchbench.schemas import RunStatus, SingleAgentOutput, TestResults


def _valid_baseline_dict():
    # Mirrors the example in the Single-Agent Baseline section.
    return {
        "bug_id": "BUG_001",
        "patch": "...",
        "tests_before": {"passed": 18, "failed": 1},
        "tests_after": {"passed": 19, "failed": 0},
        "runtime_seconds": 12,
        "token_usage": 2500,
        "status": "SUCCESS",
    }


def test_parses_doc_example():
    out = SingleAgentOutput(**_valid_baseline_dict())
    assert out.status is RunStatus.SUCCESS
    assert isinstance(out.tests_after, TestResults)
    assert out.tests_after.failed == 0


def test_rejects_negative_token_usage():
    data = _valid_baseline_dict()
    data["token_usage"] = -1
    with pytest.raises(ValidationError):
        SingleAgentOutput(**data)


def test_round_trip_json():
    out = SingleAgentOutput(**_valid_baseline_dict())
    assert SingleAgentOutput.model_validate_json(out.model_dump_json()) == out
