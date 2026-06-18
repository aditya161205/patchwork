"""The Run Trace schema — the complete record of one benchmark run.

Corresponds to "Schema 6: Run Trace Schema". This is the top-level artifact a
run produces: it stitches together the Locator, Fixer, Validator, and Judge
outputs along with routing/budget bookkeeping.

Design note: the doc shows the nested agent outputs as ``"..."`` placeholders.
We store the *actual typed sub-models* instead. The serialized JSON is the same
shape, but the trace is now self-validating end to end and far easier to work
with in later milestones. The fields are optional so a trace can be persisted
incrementally as each stage completes (or after an early failure).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from patchbench.schemas.enums import BugType, Complexity, FixerType, RunStatus
from patchbench.schemas.fixer import FixerOutput
from patchbench.schemas.judge import JudgeOutput
from patchbench.schemas.locator import LocatorOutput
from patchbench.schemas.validator import ValidatorOutput


class RunTrace(BaseModel):
    """End-to-end execution trace for a single bug repair run."""

    run_id: str = Field(..., min_length=1)
    bug_id: str = Field(..., min_length=1)
    bug_type: BugType
    complexity: Complexity
    selected_fixer: FixerType
    tool_calls: int = Field(default=0, ge=0)
    subagents_spawned: int = Field(default=0, ge=0)
    locator_output: LocatorOutput | None = None
    fixer_output: FixerOutput | None = None
    validator_output: ValidatorOutput | None = None
    judge_output: JudgeOutput | None = None
    final_status: RunStatus
