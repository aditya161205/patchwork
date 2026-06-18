"""The Fixer output schema — a candidate patch from any specialized Fixer.

Corresponds to "Schema 3: Fixer Output Schema". Every Fixer agent (Syntax,
Logic, API, State, Config, Performance) returns the same shape, tagged with
``fixer_type`` so the trace records which specialist produced the patch.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from patchbench.schemas.enums import FixerType


class FixerOutput(BaseModel):
    """A single candidate repair produced by a Fixer agent."""

    bug_id: str = Field(..., min_length=1)
    fixer_type: FixerType
    files_modified: list[str] = Field(default_factory=list)
    patch: str = Field(..., description="Unified diff to be applied to the repo.")
    confidence: float = Field(..., ge=0.0, le=1.0)
    root_cause: str
    explanation: str
