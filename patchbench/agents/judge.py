"""Judge agent — scores repair attempts using multiple quality metrics."""

from __future__ import annotations

from patchbench.schemas import Bug, FixerOutput, ValidatorOutput, JudgeOutput
from patchbench.schemas.enums import CheckStatus, RunStatus
from patchbench.metrics.scoring import compute_judge_score


class Judge:
    """Evaluates a repair attempt and produces a quantitative score.

    The Judge considers:
    - Whether the fix passes all tests (fix_rate)
    - Whether it introduced regressions
    - Code quality (lint, static analysis)
    - Patch conciseness
    - Runtime efficiency
    """

    def evaluate(
        self,
        bug: Bug,
        fixer_output: FixerOutput,
        validator_output: ValidatorOutput,
        runtime_seconds: float,
        token_usage: int,
    ) -> JudgeOutput:
        """Score a completed repair attempt."""
        tests_passed = validator_output.validation_status == CheckStatus.PASS
        no_regressions = validator_output.tests_after.failed == 0
        lint_passed = validator_output.lint_status == CheckStatus.PASS

        patch_lines = len(fixer_output.patch.splitlines()) if fixer_output.patch else 0
        files_modified = len(fixer_output.files_modified)

        regressions = max(
            0,
            validator_output.tests_before.passed - validator_output.tests_after.passed
        )

        fix_rate_val = 1.0 if tests_passed else 0.0

        score = compute_judge_score(
            tests_passed=tests_passed,
            no_regressions=no_regressions,
            lint_passed=lint_passed,
            patch_size_lines=patch_lines,
            runtime_seconds=runtime_seconds,
            files_modified=files_modified,
        )

        status = RunStatus.SUCCESS if tests_passed else RunStatus.FAILURE

        return JudgeOutput(
            bug_id=bug.bug_id,
            fix_rate=fix_rate_val,
            runtime_seconds=runtime_seconds,
            token_usage=token_usage,
            files_modified=files_modified,
            patch_size_lines=patch_lines,
            regressions=regressions,
            judge_score=score,
            status=status,
        )
