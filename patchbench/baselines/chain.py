"""Chain Baseline — sequential locate-then-fix pipeline without routing.

This baseline uses the Locator and a generic fixer (LogicFixer) sequentially,
without the Orchestrator's bug classification and specialized routing.
"""

from __future__ import annotations

import time

from patchbench.schemas import Bug, SingleAgentOutput, TestResults
from patchbench.schemas.enums import RunStatus
from patchbench.agents.locator import Locator
from patchbench.agents.fixer import LogicFixer
from patchbench.agents.validator import Validator
from patchbench.tools.test_runner import run_tests


class ChainBaseline:
    """Chain baseline: Locator -> generic Fixer -> Validator (no routing).

    Unlike the multi-agent system, the chain always uses LogicFixer regardless
    of bug type, testing whether specialized routing adds value.
    """

    def __init__(self, timeout: int = 60) -> None:
        self.timeout = timeout
        self.locator = Locator()
        self.fixer = LogicFixer()
        self.validator = Validator(timeout=timeout)

    def run(self, bug: Bug, repo_path: str) -> SingleAgentOutput:
        """Execute the chain baseline pipeline."""
        start = time.time()

        # Run tests before
        before_result = run_tests(repo_path, bug.failing_tests, timeout=self.timeout)
        tests_before = TestResults(passed=before_result.passed, failed=before_result.failed)

        # Locate
        locator_output = self.locator.locate(bug, repo_path)

        # Fix (always uses LogicFixer)
        fixer_output = self.fixer.fix(bug, locator_output, repo_path)

        # Validate
        validator_output = self.validator.validate(bug, fixer_output, repo_path)

        tests_after = validator_output.tests_after
        runtime = time.time() - start
        status = RunStatus.SUCCESS if validator_output.tests_after.failed == 0 else RunStatus.FAILURE

        return SingleAgentOutput(
            bug_id=bug.bug_id,
            patch=fixer_output.patch,
            tests_before=tests_before,
            tests_after=tests_after,
            runtime_seconds=round(runtime, 2),
            token_usage=0,
            status=status,
        )
