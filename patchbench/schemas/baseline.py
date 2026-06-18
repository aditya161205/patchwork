"""The Single-Agent Baseline output schema.

Corresponds to the "Output Schema" in the Single-Agent Baseline section. The
single LLM-call baseline does no localization/judging of its own, so its output
is a slim record: the patch plus before/after test counts and run cost.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from patchbench.schemas.enums import RunStatus
from patchbench.schemas.validator import TestResults


class SingleAgentOutput(BaseModel):
    """Result of a single-LLM-call repair attempt."""

    bug_id: str = Field(..., min_length=1)
    patch: str
    tests_before: TestResults
    tests_after: TestResults
    runtime_seconds: float = Field(..., ge=0.0)
    token_usage: int = Field(..., ge=0)
    status: RunStatus
