"""Tests for the approval gate."""

from patchbench.schemas import Bug, FixerOutput, ValidatorOutput, TestResults
from patchbench.schemas.enums import BugType, CheckStatus, Difficulty, FixerType
from patchbench.runner.approval import ApprovalGate, ApprovalDecision


def _bug():
    return Bug(
        bug_id="TEST_001",
        title="Test bug",
        bug_type=BugType.LOGICAL_ERROR,
        difficulty=Difficulty.EASY,
        repo_path="test/repo",
        issue_description="Test",
        failing_tests=["test_foo"],
        expected_behavior="works",
        actual_behavior="broken",
    )


def _fixer_output():
    return FixerOutput(
        bug_id="TEST_001",
        fixer_type=FixerType.LOGIC_FIXER,
        files_modified=["foo.py"],
        patch="--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-bad\n+good\n",
        confidence=0.8,
        root_cause="wrong operator",
        explanation="fixed it",
    )


def _validator_output():
    return ValidatorOutput(
        bug_id="TEST_001",
        validation_status=CheckStatus.PASS,
        tests_before=TestResults(passed=10, failed=1),
        tests_after=TestResults(passed=11, failed=0),
        lint_status=CheckStatus.PASS,
        static_analysis_status=CheckStatus.PASS,
        validation_report="All good",
    )


def test_auto_approve():
    gate = ApprovalGate(auto_approve=True)
    decision = gate.request_approval(_bug(), _fixer_output(), _validator_output())
    assert decision.approved is True
    assert decision.reason == "auto-approved"


def test_custom_approver():
    def always_reject(bug, fixer, validator):
        return ApprovalDecision(approved=False, reason="policy")

    gate = ApprovalGate(approver=always_reject)
    decision = gate.request_approval(_bug(), _fixer_output(), _validator_output())
    assert decision.approved is False
    assert decision.reason == "policy"


def test_custom_approver_approve():
    def always_approve(bug, fixer, validator):
        return ApprovalDecision(approved=True, reason="lgtm")

    gate = ApprovalGate(approver=always_approve)
    decision = gate.request_approval(_bug(), _fixer_output(), _validator_output())
    assert decision.approved is True
