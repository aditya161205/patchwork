"""The Bug schema — a single benchmark repair task.

Corresponds to "Schema 1: Bug Schema" in the design doc. A ``Bug`` is the input
to the whole pipeline: it points at a synthetic repository and describes the
defect, the failing tests, and the expected vs. actual behavior.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from patchbench.schemas.enums import BugType, Difficulty


class Bug(BaseModel):
    """A benchmark bug task loaded from the dataset."""

    bug_id: str = Field(..., min_length=1, description="Stable id, e.g. 'BUG_001'.")
    title: str = Field(..., min_length=1)
    bug_type: BugType
    difficulty: Difficulty
    repo_path: str = Field(
        ..., min_length=1, description="Path to the synthetic repo, e.g. 'repos/cart_app'."
    )
    issue_description: str
    stack_trace: str | None = Field(
        default=None, description="Optional captured stack trace / logs."
    )
    failing_tests: list[str] = Field(
        default_factory=list, description="Test ids/names known to fail before the fix."
    )
    expected_behavior: str
    actual_behavior: str
