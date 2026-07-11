"""Orchestrator agent — classifies bugs and routes to specialized fixers."""

from __future__ import annotations

from patchbench.schemas import Bug, LocatorOutput, FixerOutput, ValidatorOutput, JudgeOutput
from patchbench.schemas.enums import BugType, Complexity, FixerType, RunStatus
from patchbench.schemas.trace import RunTrace

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
    """Routes a bug to the appropriate specialized fixer based on bug type.

    The Orchestrator:
    1. Classifies the bug (uses metadata bug_type)
    2. Estimates complexity
    3. Selects the appropriate fixer
    4. Coordinates the pipeline: Locator -> Fixer -> Validator -> Judge
    """

    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max_retries

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

    def create_trace(
        self,
        *,
        run_id: str,
        bug: Bug,
        fixer_type: FixerType,
        complexity: Complexity,
        locator_output: LocatorOutput | None = None,
        fixer_output: FixerOutput | None = None,
        validator_output: ValidatorOutput | None = None,
        judge_output: JudgeOutput | None = None,
        tool_calls: int = 0,
        subagents_spawned: int = 0,
        final_status: RunStatus = RunStatus.FAILURE,
    ) -> RunTrace:
        """Create the run trace record for a pipeline execution."""
        return RunTrace(
            run_id=run_id,
            bug_id=bug.bug_id,
            bug_type=bug.bug_type,
            complexity=complexity,
            selected_fixer=fixer_type,
            tool_calls=tool_calls,
            subagents_spawned=subagents_spawned,
            locator_output=locator_output,
            fixer_output=fixer_output,
            validator_output=validator_output,
            judge_output=judge_output,
            final_status=final_status,
        )
