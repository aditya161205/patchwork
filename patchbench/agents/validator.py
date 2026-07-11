"""Validator agent — verifies fixes in a sandboxed environment.

Uses the full verifier pipeline: sandbox isolation, fail-to-pass analysis,
regression detection, lint, static analysis, and cheat detection.
"""

from __future__ import annotations

from patchbench.schemas import Bug, FixerOutput, ValidatorOutput, TestResults
from patchbench.schemas.enums import CheckStatus
from patchbench.tools.verifier import verify_patch, VerificationResult
from patchbench.tools.cheat_detector import is_clean


class Validator:
    """Validates a proposed patch using sandboxed execution.

    The Validator:
    1. Copies the repo to a temp directory (sandbox)
    2. Runs failing tests to confirm they fail (baseline)
    3. Runs all tests to get pass-to-pass baseline
    4. Applies the patch in the sandbox
    5. Runs failing tests again (fail-to-pass check)
    6. Runs all tests again (regression detection)
    7. Runs lint and static analysis
    8. Checks for cheating (test-file edits, hardcoded values)
    9. Reports verdict: PASS / FAIL / CHEATED

    The original repository is NEVER modified.
    """

    def __init__(self, timeout: int = 60) -> None:
        self.timeout = timeout

    def validate(
        self,
        bug: Bug,
        fixer_output: FixerOutput,
        repo_path: str,
    ) -> ValidatorOutput:
        """Run full sandboxed validation pipeline on a proposed fix."""
        # Run cheat check first (fast, no sandbox needed)
        patch = fixer_output.patch
        clean = is_clean(patch, bug.failing_tests)

        # Run full verification in sandbox
        result = verify_patch(
            repo_path=repo_path,
            patch=patch,
            failing_tests=bug.failing_tests,
            timeout=self.timeout,
        )

        # Map to schema
        tests_before = TestResults(
            passed=result.tests_before_passed,
            failed=result.tests_before_failed,
        )
        tests_after = TestResults(
            passed=result.tests_after_passed,
            failed=result.tests_after_failed,
        )

        lint_status = CheckStatus.PASS if result.lint_passed else CheckStatus.FAIL
        sa_status = CheckStatus.PASS if result.static_analysis_passed else CheckStatus.FAIL

        if result.verdict == "PASS":
            validation_status = CheckStatus.PASS
        else:
            validation_status = CheckStatus.FAIL

        report = self._build_report(result)

        return ValidatorOutput(
            bug_id=bug.bug_id,
            validation_status=validation_status,
            tests_before=tests_before,
            tests_after=tests_after,
            lint_status=lint_status,
            static_analysis_status=sa_status,
            validation_report=report,
        )

    def _build_report(self, result: VerificationResult) -> str:
        parts = []
        parts.append(f"Verdict: {result.verdict}")
        parts.append(f"Patch applied: {result.patch_applied}")
        parts.append(
            f"Fail-to-pass: {result.fail_to_pass_resolved}/{result.fail_to_pass_total} "
            f"({result.fail_to_pass_rate:.0%})"
        )
        parts.append(
            f"Pass-to-pass: {result.pass_to_pass_maintained}/{result.pass_to_pass_total} "
            f"({result.pass_to_pass_rate:.0%})"
        )
        parts.append(f"Regressions: {result.regressions}")
        parts.append(f"Lint: {'PASS' if result.lint_passed else 'FAIL'}")
        parts.append(f"Static analysis: {'PASS' if result.static_analysis_passed else 'FAIL'}")
        if result.cheat_flags:
            parts.append(f"Cheat flags: {len(result.cheat_flags)}")
            for flag in result.cheat_flags:
                parts.append(f"  [{flag.severity}] {flag.rule}: {flag.description}")
        return "\n".join(parts)
