"""The Validator output schema — result of applying and testing a patch.

Corresponds to "Schema 4: Validator Output Schema". The Validator runs the test
suite before and after the patch, plus lint and static-analysis checks, and
emits an overall PASS/FAIL verdict.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from patchbench.schemas.enums import CheckStatus


class TestResults(BaseModel):
    """Pass/fail counts from a single test-suite execution.

    Shared by the Validator (before/after) and the single-agent baseline.
    """

    passed: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)


class ValidatorOutput(BaseModel):
    """Validation results after a patch has been applied."""

    bug_id: str = Field(..., min_length=1)
    validation_status: CheckStatus
    tests_before: TestResults
    tests_after: TestResults
    lint_status: CheckStatus
    static_analysis_status: CheckStatus
    validation_report: str = ""
