"""Human approval gate — show diff and wait for yes/no before applying.

Provides both interactive (terminal) and programmatic approval modes.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable

from patchbench.schemas import Bug, FixerOutput, ValidatorOutput


@dataclass
class ApprovalDecision:
    """The human's decision on a proposed patch."""

    approved: bool
    reason: str = ""


class ApprovalGate:
    """Interactive approval gate that shows a diff and waits for human input.

    In auto_approve mode, all patches are approved (for batch benchmarking).
    In interactive mode, the diff is printed and the user is prompted.
    """

    def __init__(self, auto_approve: bool = False, approver: Callable[..., ApprovalDecision] | None = None) -> None:
        self.auto_approve = auto_approve
        self._custom_approver = approver

    def request_approval(
        self,
        bug: Bug,
        fixer_output: FixerOutput,
        validator_output: ValidatorOutput,
    ) -> ApprovalDecision:
        """Show the proposed fix and get human approval."""
        if self.auto_approve:
            return ApprovalDecision(approved=True, reason="auto-approved")

        if self._custom_approver:
            return self._custom_approver(bug, fixer_output, validator_output)

        return self._interactive_approval(bug, fixer_output, validator_output)

    def _interactive_approval(
        self,
        bug: Bug,
        fixer_output: FixerOutput,
        validator_output: ValidatorOutput,
    ) -> ApprovalDecision:
        """Terminal-based interactive approval."""
        print("\n" + "=" * 70)
        print(f"  APPROVAL REQUIRED: {bug.bug_id} — {bug.title}")
        print("=" * 70)
        print(f"\n  Bug type: {bug.bug_type.value}")
        print(f"  Fixer: {fixer_output.fixer_type.value}")
        print(f"  Root cause: {fixer_output.root_cause}")
        print(f"  Confidence: {fixer_output.confidence:.0%}")
        print(f"  Files modified: {', '.join(fixer_output.files_modified)}")
        print(f"\n  Validation: {validator_output.validation_status.value}")
        print(f"  Tests: {validator_output.tests_after.passed} passed, "
              f"{validator_output.tests_after.failed} failed")
        print(f"\n{'─' * 70}")
        print("  PROPOSED PATCH:")
        print(f"{'─' * 70}")

        for line in fixer_output.patch.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                print(f"  \033[32m{line}\033[0m")
            elif line.startswith("-") and not line.startswith("---"):
                print(f"  \033[31m{line}\033[0m")
            else:
                print(f"  {line}")

        print(f"\n{'─' * 70}")

        while True:
            try:
                response = input("\n  Apply this patch? [y]es / [n]o / [s]kip: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return ApprovalDecision(approved=False, reason="interrupted")

            if response in ("y", "yes"):
                return ApprovalDecision(approved=True, reason="human-approved")
            elif response in ("n", "no"):
                reason = input("  Reason (optional): ").strip()
                return ApprovalDecision(approved=False, reason=reason or "human-rejected")
            elif response in ("s", "skip"):
                return ApprovalDecision(approved=False, reason="skipped")
            else:
                print("  Please enter y, n, or s.")
