"""Scoring functions for PatchBench evaluation.

Metrics:
- Fix Rate: fraction of bugs successfully fixed (binary per bug)
- Regression Rate: fraction of previously passing tests that now fail
- Overall Repair Score: composite 0-10 score combining multiple factors
"""

from __future__ import annotations

from patchbench.schemas import JudgeOutput, ValidatorOutput, TestResults


def fix_rate(judge_outputs: list[JudgeOutput]) -> float:
    """Compute fleet-wide fix rate: fraction of bugs fixed."""
    if not judge_outputs:
        return 0.0
    return sum(j.fix_rate for j in judge_outputs) / len(judge_outputs)


def regression_rate(tests_before: TestResults, tests_after: TestResults) -> float:
    """Compute regression rate: fraction of previously-passing tests that now fail.

    A regression happens when tests that passed before the patch now fail after.
    """
    if tests_before.passed == 0:
        return 0.0
    regressions = max(0, tests_before.passed - tests_after.passed)
    return regressions / tests_before.passed


def overall_repair_score(judge_outputs: list[JudgeOutput]) -> float:
    """Compute the average Overall Repair Score across all bugs (0-10 scale)."""
    if not judge_outputs:
        return 0.0
    return sum(j.judge_score for j in judge_outputs) / len(judge_outputs)


def compute_judge_score(
    *,
    tests_passed: bool,
    no_regressions: bool,
    lint_passed: bool,
    patch_size_lines: int,
    runtime_seconds: float,
    files_modified: int,
) -> float:
    """Compute the composite judge score (0-10) for a single repair attempt.

    Scoring breakdown:
    - Tests pass (fix works): 4 points
    - No regressions: 2 points
    - Lint clean: 1 point
    - Patch conciseness (fewer lines = better): up to 1.5 points
    - Speed (faster = better): up to 1 point
    - Minimal file changes: up to 0.5 points
    """
    score = 0.0

    if tests_passed:
        score += 4.0
    if no_regressions:
        score += 2.0
    if lint_passed:
        score += 1.0

    if patch_size_lines <= 5:
        score += 1.5
    elif patch_size_lines <= 15:
        score += 1.0
    elif patch_size_lines <= 50:
        score += 0.5

    if runtime_seconds < 10:
        score += 1.0
    elif runtime_seconds < 30:
        score += 0.7
    elif runtime_seconds < 60:
        score += 0.4

    if files_modified == 1:
        score += 0.5
    elif files_modified <= 3:
        score += 0.25

    return min(10.0, round(score, 2))
