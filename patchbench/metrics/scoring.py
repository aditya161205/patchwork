"""Scoring functions for PatchBench evaluation.

10 Metrics:
1. Fix Rate: fraction of bugs successfully fixed (binary per bug)
2. Fail-to-Pass Rate: fraction of target failing tests that now pass
3. Pass-to-Pass Rate: fraction of previously passing tests still passing
4. Regression Rate: fraction of previously passing tests that now fail
5. Localization Accuracy: whether the locator found the actual buggy file
6. Patch Minimality: inverse of patch size (smaller = better)
7. Token Efficiency: fix quality per token used
8. Runtime Efficiency: fix quality per second
9. Cheat-Free Rate: fraction of patches that pass cheat detection
10. Overall Repair Score: composite 0-10 score combining multiple factors
"""

from __future__ import annotations

from patchbench.schemas import JudgeOutput, TestResults


def fix_rate(judge_outputs: list[JudgeOutput]) -> float:
    """1. Fleet-wide fix rate: fraction of bugs fixed."""
    if not judge_outputs:
        return 0.0
    return sum(j.fix_rate for j in judge_outputs) / len(judge_outputs)


def fail_to_pass_rate(resolved: int, total: int) -> float:
    """2. Fraction of target failing tests resolved by the patch."""
    if total == 0:
        return 0.0
    return resolved / total


def pass_to_pass_rate(maintained: int, total: int) -> float:
    """3. Fraction of previously passing tests still passing after patch."""
    if total == 0:
        return 1.0
    return maintained / total


def regression_rate(tests_before: TestResults, tests_after: TestResults) -> float:
    """4. Fraction of previously-passing tests that now fail."""
    if tests_before.passed == 0:
        return 0.0
    regressions = max(0, tests_before.passed - tests_after.passed)
    return regressions / tests_before.passed


def localization_accuracy(candidate_files: list[str], ground_truth_files: list[str]) -> float:
    """5. Whether the locator found the actual buggy file(s).

    Returns fraction of ground truth files that appear in the candidate list.
    """
    if not ground_truth_files:
        return 0.0
    found = sum(1 for gt in ground_truth_files if gt in candidate_files)
    return found / len(ground_truth_files)


def patch_minimality(patch_lines: int, max_acceptable: int = 50) -> float:
    """6. Patch minimality score (0-1). Smaller patches score higher.

    A 1-line patch scores 1.0. A patch at max_acceptable scores ~0.0.
    """
    if patch_lines <= 0:
        return 0.0
    return max(0.0, 1.0 - (patch_lines - 1) / max_acceptable)


def token_efficiency(judge_score: float, token_usage: int) -> float:
    """7. Fix quality per 1000 tokens used. Higher = more efficient."""
    if token_usage == 0:
        return judge_score
    return judge_score / (token_usage / 1000)


def runtime_efficiency(judge_score: float, runtime_seconds: float) -> float:
    """8. Fix quality per second. Higher = faster fixes."""
    if runtime_seconds <= 0:
        return judge_score
    return judge_score / runtime_seconds


def cheat_free_rate(clean_count: int, total: int) -> float:
    """9. Fraction of patches that passed cheat detection."""
    if total == 0:
        return 0.0
    return clean_count / total


def overall_repair_score(judge_outputs: list[JudgeOutput]) -> float:
    """10. Average Overall Repair Score across all bugs (0-10 scale)."""
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


def compute_all_metrics(judge_outputs: list[JudgeOutput]) -> dict[str, float]:
    """Compute all 10 metrics from a list of judge outputs."""
    return {
        "fix_rate": fix_rate(judge_outputs),
        "overall_repair_score": overall_repair_score(judge_outputs),
        "avg_runtime": (
            sum(j.runtime_seconds for j in judge_outputs) / len(judge_outputs)
            if judge_outputs else 0.0
        ),
        "avg_patch_size": (
            sum(j.patch_size_lines for j in judge_outputs) / len(judge_outputs)
            if judge_outputs else 0.0
        ),
        "avg_token_usage": (
            sum(j.token_usage for j in judge_outputs) / len(judge_outputs)
            if judge_outputs else 0.0
        ),
        "total_regressions": sum(j.regressions for j in judge_outputs),
        "avg_files_modified": (
            sum(j.files_modified for j in judge_outputs) / len(judge_outputs)
            if judge_outputs else 0.0
        ),
    }
