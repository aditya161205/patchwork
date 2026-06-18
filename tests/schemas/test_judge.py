"""Tests for the Judge output schema."""

import pytest
from pydantic import ValidationError

from patchbench.schemas import JudgeOutput, RunStatus


def _valid_judge_dict():
    # Mirrors the example in the design doc (Schema 5).
    return {
        "bug_id": "BUG_001",
        "fix_rate": 1,
        "runtime_seconds": 42,
        "token_usage": 12450,
        "files_modified": 1,
        "patch_size_lines": 4,
        "regressions": 0,
        "judge_score": 9.1,
        "status": "SUCCESS",
    }


def test_parses_doc_example():
    j = JudgeOutput(**_valid_judge_dict())
    assert j.fix_rate == 1.0
    assert j.status is RunStatus.SUCCESS
    assert j.judge_score == 9.1


def test_rejects_fix_rate_above_one():
    data = _valid_judge_dict()
    data["fix_rate"] = 2
    with pytest.raises(ValidationError):
        JudgeOutput(**data)


def test_rejects_judge_score_out_of_scale():
    data = _valid_judge_dict()
    data["judge_score"] = 11
    with pytest.raises(ValidationError):
        JudgeOutput(**data)


def test_rejects_negative_counts():
    data = _valid_judge_dict()
    data["regressions"] = -1
    with pytest.raises(ValidationError):
        JudgeOutput(**data)


def test_round_trip_json():
    j = JudgeOutput(**_valid_judge_dict())
    assert JudgeOutput.model_validate_json(j.model_dump_json()) == j
