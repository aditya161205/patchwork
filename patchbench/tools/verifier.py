"""Full verifier — sandbox + cheat detection + fail-to-pass/pass-to-pass analysis.

This is the production verification backbone that:
1. Runs in a sandboxed copy (original repo never touched)
2. Distinguishes fail-to-pass (target tests that were failing now pass)
   from pass-to-pass (previously passing tests still pass)
3. Detects regressions (previously passing tests now fail)
4. Runs cheat detection on the patch
5. Produces a detailed VerificationResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from patchbench.tools.sandbox import sandboxed_repo
from patchbench.tools.patch_apply import apply_patch
from patchbench.tools.test_runner import run_tests, TestRunResult
from patchbench.tools.linter import run_lint, LintResult
from patchbench.tools.static_analysis import run_static_analysis, StaticAnalysisResult
from patchbench.tools.cheat_detector import detect_cheats, CheatFlag


@dataclass
class VerificationResult:
    """Detailed verification result with fail-to-pass analysis."""

    patch_applied: bool

    # Fail-to-pass: the target failing tests that now pass after the fix
    fail_to_pass_total: int
    fail_to_pass_resolved: int

    # Pass-to-pass: previously passing tests that still pass (no regressions)
    pass_to_pass_total: int
    pass_to_pass_maintained: int

    # Regressions: previously passing tests that now fail
    regressions: int

    # Full test counts
    tests_before_passed: int
    tests_before_failed: int
    tests_after_passed: int
    tests_after_failed: int

    # Quality checks
    lint_passed: bool
    static_analysis_passed: bool

    # Cheat detection
    cheat_flags: list[CheatFlag] = field(default_factory=list)
    is_clean: bool = True

    # Overall verdict
    verdict: str = "FAIL"  # "PASS", "FAIL", "CHEATED"

    @property
    def fail_to_pass_rate(self) -> float:
        if self.fail_to_pass_total == 0:
            return 0.0
        return self.fail_to_pass_resolved / self.fail_to_pass_total

    @property
    def pass_to_pass_rate(self) -> float:
        if self.pass_to_pass_total == 0:
            return 1.0
        return self.pass_to_pass_maintained / self.pass_to_pass_total

    @property
    def regression_rate(self) -> float:
        if self.pass_to_pass_total == 0:
            return 0.0
        return self.regressions / self.pass_to_pass_total


def verify_patch(
    repo_path: str,
    patch: str,
    failing_tests: list[str],
    timeout: int = 60,
) -> VerificationResult:
    """Run full verification pipeline in a sandbox.

    Steps:
    1. Copy repo to sandbox
    2. Run ONLY the failing tests (before) — count how many actually fail
    3. Run ALL tests (before) — count passes for pass-to-pass baseline
    4. Apply patch
    5. Run ONLY the previously-failing tests (after) — count fail-to-pass
    6. Run ALL tests (after) — count pass-to-pass and regressions
    7. Run lint + static analysis
    8. Run cheat detectors on the patch text
    9. Compute verdict
    """
    # Cheat detection (doesn't need sandbox)
    cheat_flags = detect_cheats(patch, failing_tests)
    has_critical_cheat = any(f.severity == "critical" for f in cheat_flags)

    with sandboxed_repo(repo_path) as sandbox:
        # Run failing tests before patch (to confirm they actually fail)
        failing_before = run_tests(sandbox, failing_tests, timeout=timeout)
        fail_to_pass_total = failing_before.failed

        # Run all tests before patch (baseline for pass-to-pass)
        all_before = run_tests(sandbox, timeout=timeout)
        pass_to_pass_total = all_before.passed

        # Apply patch
        patch_applied = False
        if patch:
            patch_applied = apply_patch(sandbox, patch)

        if not patch_applied:
            return VerificationResult(
                patch_applied=False,
                fail_to_pass_total=fail_to_pass_total,
                fail_to_pass_resolved=0,
                pass_to_pass_total=pass_to_pass_total,
                pass_to_pass_maintained=pass_to_pass_total,
                regressions=0,
                tests_before_passed=all_before.passed,
                tests_before_failed=all_before.failed,
                tests_after_passed=all_before.passed,
                tests_after_failed=all_before.failed,
                lint_passed=True,
                static_analysis_passed=True,
                cheat_flags=cheat_flags,
                is_clean=not has_critical_cheat,
                verdict="FAIL",
            )

        # Run failing tests after patch (fail-to-pass check)
        failing_after = run_tests(sandbox, failing_tests, timeout=timeout)
        fail_to_pass_resolved = fail_to_pass_total - failing_after.failed

        # Run all tests after patch (pass-to-pass + regression check)
        all_after = run_tests(sandbox, timeout=timeout)
        regressions = max(0, all_before.passed - (all_after.passed - fail_to_pass_resolved))
        regressions = min(regressions, pass_to_pass_total)
        pass_to_pass_maintained = pass_to_pass_total - regressions

        # Lint and static analysis
        lint_result = run_lint(sandbox)
        sa_result = run_static_analysis(sandbox)

        # Compute verdict
        all_target_fixed = failing_after.failed == 0
        no_regressions = regressions == 0

        if has_critical_cheat:
            verdict = "CHEATED"
        elif all_target_fixed and no_regressions:
            verdict = "PASS"
        else:
            verdict = "FAIL"

        return VerificationResult(
            patch_applied=True,
            fail_to_pass_total=fail_to_pass_total,
            fail_to_pass_resolved=fail_to_pass_resolved,
            pass_to_pass_total=pass_to_pass_total,
            pass_to_pass_maintained=pass_to_pass_maintained,
            regressions=regressions,
            tests_before_passed=all_before.passed,
            tests_before_failed=all_before.failed,
            tests_after_passed=all_after.passed,
            tests_after_failed=all_after.failed,
            lint_passed=lint_result.passed,
            static_analysis_passed=sa_result.passed,
            cheat_flags=cheat_flags,
            is_clean=not has_critical_cheat,
            verdict=verdict,
        )
