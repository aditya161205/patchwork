"""The Judge output schema — per-bug benchmark evaluation.

Corresponds to "Schema 5: Judge Output Schema". The Judge agent turns a single
repair attempt into the quantitative metrics PatchBench compares across agent
architectures.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from patchbench.schemas.enums import RunStatus


class JudgeOutput(BaseModel):
    """Scored evaluation of one repair attempt.

    ``fix_rate`` is binary per bug (1.0 fixed / 0.0 not) and aggregates into the
    fleet-wide Fix Rate metric. ``judge_score`` is the composite Overall Repair
    Score on a 0-10 scale.
    """

    bug_id: str = Field(..., min_length=1)
    fix_rate: float = Field(..., ge=0.0, le=1.0)
    runtime_seconds: float = Field(..., ge=0.0)
    token_usage: int = Field(..., ge=0)
    files_modified: int = Field(..., ge=0)
    patch_size_lines: int = Field(..., ge=0)
    regressions: int = Field(..., ge=0)
    judge_score: float = Field(..., ge=0.0, le=10.0)
    status: RunStatus
