"""Tests for the metrics package."""

from patchbench.schemas import JudgeOutput, TestResults
from patchbench.schemas.enums import RunStatus
from patchbench.metrics import fix_rate, regression_rate, overall_repair_score, compute_judge_score


def _judge(bug_id: str, fixed: bool) -> JudgeOutput:
    return JudgeOutput(
        bug_id=bug_id,
        fix_rate=1.0 if fixed else 0.0,
        runtime_seconds=5.0,
        token_usage=100,
        files_modified=1,
        patch_size_lines=5,
        regressions=0,
        judge_score=8.0 if fixed else 2.0,
        status=RunStatus.SUCCESS if fixed else RunStatus.FAILURE,
    )


def test_fix_rate_all_fixed():
    judges = [_judge("BUG_1", True), _judge("BUG_2", True)]
    assert fix_rate(judges) == 1.0


def test_fix_rate_none_fixed():
    judges = [_judge("BUG_1", False), _judge("BUG_2", False)]
    assert fix_rate(judges) == 0.0


def test_fix_rate_half_fixed():
    judges = [_judge("BUG_1", True), _judge("BUG_2", False)]
    assert fix_rate(judges) == 0.5


def test_fix_rate_empty():
    assert fix_rate([]) == 0.0


def test_regression_rate_no_regressions():
    before = TestResults(passed=10, failed=2)
    after = TestResults(passed=12, failed=0)
    assert regression_rate(before, after) == 0.0


def test_regression_rate_some_regressions():
    before = TestResults(passed=10, failed=0)
    after = TestResults(passed=8, failed=2)
    assert regression_rate(before, after) == 0.2


def test_overall_repair_score():
    judges = [_judge("BUG_1", True), _judge("BUG_2", False)]
    assert overall_repair_score(judges) == 5.0


def test_compute_judge_score_perfect():
    score = compute_judge_score(
        tests_passed=True,
        no_regressions=True,
        lint_passed=True,
        patch_size_lines=3,
        runtime_seconds=5.0,
        files_modified=1,
    )
    assert score == 10.0


def test_compute_judge_score_failed():
    score = compute_judge_score(
        tests_passed=False,
        no_regressions=False,
        lint_passed=False,
        patch_size_lines=100,
        runtime_seconds=120.0,
        files_modified=5,
    )
    assert score == 0.0
