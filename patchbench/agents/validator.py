"""Validator agent — applies patches and runs tests to verify fixes."""

from __future__ import annotations

from patchbench.schemas import Bug, FixerOutput, ValidatorOutput, TestResults
from patchbench.schemas.enums import CheckStatus
from patchbench.tools.test_runner import run_tests
from patchbench.tools.patch_apply import apply_patch, revert_patch
from patchbench.tools.linter import run_lint
from patchbench.tools.static_analysis import run_static_analysis


class Validator:
    """Validates a proposed patch by running tests before and after application.

    The Validator:
    1. Runs tests on the original (buggy) code to get baseline counts
    2. Applies the patch
    3. Runs tests again to see if the fix works
    4. Runs lint and static analysis checks
    5. Reports an overall PASS/FAIL verdict
    """

    def __init__(self, timeout: int = 60) -> None:
        self.timeout = timeout

    def validate(
        self,
        bug: Bug,
        fixer_output: FixerOutput,
        repo_path: str,
    ) -> ValidatorOutput:
        """Run validation pipeline on a proposed fix."""
        # Run tests before patch
        before_result = run_tests(repo_path, bug.failing_tests, timeout=self.timeout)
        tests_before = TestResults(passed=before_result.passed, failed=before_result.failed)

        # Apply patch
        patch_applied = False
        if fixer_output.patch:
            patch_applied = apply_patch(repo_path, fixer_output.patch)

        # Run tests after patch
        if patch_applied:
            after_result = run_tests(repo_path, timeout=self.timeout)
            tests_after = TestResults(passed=after_result.passed, failed=after_result.failed)
        else:
            tests_after = tests_before

        # Lint check
        lint_result = run_lint(repo_path, fixer_output.files_modified or None)
        lint_status = CheckStatus.PASS if lint_result.passed else CheckStatus.FAIL

        # Static analysis
        sa_result = run_static_analysis(repo_path, fixer_output.files_modified or None)
        sa_status = CheckStatus.PASS if sa_result.passed else CheckStatus.FAIL

        # Overall verdict
        tests_pass = tests_after.failed == 0
        validation_status = CheckStatus.PASS if (tests_pass and patch_applied) else CheckStatus.FAIL

        # Revert patch to restore original state
        if patch_applied:
            revert_patch(repo_path, fixer_output.patch)

        report = self._build_report(
            patch_applied, tests_before, tests_after, lint_result.issues, sa_result.issues
        )

        return ValidatorOutput(
            bug_id=bug.bug_id,
            validation_status=validation_status,
            tests_before=tests_before,
            tests_after=tests_after,
            lint_status=lint_status,
            static_analysis_status=sa_status,
            validation_report=report,
        )

    def _build_report(
        self,
        patch_applied: bool,
        tests_before: TestResults,
        tests_after: TestResults,
        lint_issues: list[str],
        sa_issues: list[str],
    ) -> str:
        parts = []
        if not patch_applied:
            parts.append("PATCH APPLICATION FAILED")
        parts.append(f"Tests before: {tests_before.passed} passed, {tests_before.failed} failed")
        parts.append(f"Tests after: {tests_after.passed} passed, {tests_after.failed} failed")
        if lint_issues:
            parts.append(f"Lint issues: {'; '.join(lint_issues[:5])}")
        if sa_issues:
            parts.append(f"Static analysis issues: {'; '.join(sa_issues[:5])}")
        return "\n".join(parts)
