"""Orchestrator agent — classifies bugs, routes to fixers, and manages retries."""

from __future__ import annotations

import time
import uuid

from patchbench.schemas import Bug, LocatorOutput, FixerOutput, ValidatorOutput, JudgeOutput
from patchbench.schemas.enums import BugType, CheckStatus, Complexity, FixerType, RunStatus
from patchbench.schemas.trace import RunTrace
from patchbench.agents.locator import Locator
from patchbench.agents.fixer import get_fixer, BaseFixer
from patchbench.agents.validator import Validator
from patchbench.agents.judge import Judge

BUG_TYPE_TO_FIXER: dict[BugType, FixerType] = {
    BugType.SYNTAX_ERROR: FixerType.SYNTAX_FIXER,
    BugType.LOGICAL_ERROR: FixerType.LOGIC_FIXER,
    BugType.API_MISMATCH: FixerType.API_FIXER,
    BugType.STATE_BUG: FixerType.STATE_FIXER,
    BugType.TEST_FAILURE: FixerType.LOGIC_FIXER,
    BugType.DEPENDENCY_CONFIG_BUG: FixerType.CONFIG_FIXER,
    BugType.PERFORMANCE_BUG: FixerType.PERFORMANCE_FIXER,
}


class Orchestrator:
    """Routes a bug to the appropriate specialized fixer with retry logic.

    Pipeline flow:
    1. Classify the bug type and estimate complexity
    2. Select the appropriate specialized fixer
    3. Run Locator to find candidate files/functions
    4. Run Fixer to generate a patch
    5. Run Validator to check if the patch works
    6. If FAIL and retries remain: go back to step 4
    7. Run Judge to score the final attempt
    8. Return the full RunTrace
    """

    def __init__(self, max_retries: int = 2, timeout: int = 60) -> None:
        self.max_retries = max_retries
        self.timeout = timeout
        self.locator = Locator()
        self.validator = Validator(timeout=timeout)
        self.judge = Judge()

    def run(self, bug: Bug, repo_path: str) -> RunTrace:
        """Execute the full pipeline with retry logic."""
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        start = time.time()
        tool_calls = 0

        # Step 1: Classify
        bug_type, complexity = self.classify(bug)
        fixer_type = self.select_fixer(bug_type)
        fixer = get_fixer(fixer_type)

        # Step 2: Locate
        locator_output = self.locator.locate(bug, repo_path)
        tool_calls += 1

        # Step 3: Fix + Validate with retries
        best_fixer_output: FixerOutput | None = None
        best_validator_output: ValidatorOutput | None = None

        for attempt in range(1 + self.max_retries):
            fixer_output = fixer.fix(bug, locator_output, repo_path)
            tool_calls += 1

            validator_output = self.validator.validate(bug, fixer_output, repo_path)
            tool_calls += 1

            best_fixer_output = fixer_output
            best_validator_output = validator_output

            if validator_output.validation_status == CheckStatus.PASS:
                break

        # Step 4: Judge
        runtime = time.time() - start
        judge_output = self.judge.evaluate(
            bug, best_fixer_output, best_validator_output,
            runtime_seconds=round(runtime, 2),
            token_usage=0,
        )
        tool_calls += 1

        final_status = judge_output.status

        return RunTrace(
            run_id=run_id,
            bug_id=bug.bug_id,
            bug_type=bug.bug_type,
            complexity=complexity,
            selected_fixer=fixer_type,
            tool_calls=tool_calls,
            subagents_spawned=3,
            locator_output=locator_output,
            fixer_output=best_fixer_output,
            validator_output=best_validator_output,
            judge_output=judge_output,
            final_status=final_status,
        )

    def classify(self, bug: Bug) -> tuple[BugType, Complexity]:
        """Classify bug type and estimate complexity."""
        bug_type = bug.bug_type
        complexity = self._estimate_complexity(bug)
        return bug_type, complexity

    def select_fixer(self, bug_type: BugType) -> FixerType:
        """Route bug to the appropriate specialized fixer."""
        return BUG_TYPE_TO_FIXER[bug_type]

    def _estimate_complexity(self, bug: Bug) -> Complexity:
        """Estimate whether the bug is simple or complex based on heuristics."""
        if bug.difficulty.value == "hard":
            return Complexity.COMPLEX
        if len(bug.failing_tests) > 3:
            return Complexity.COMPLEX
        return Complexity.SIMPLE
