"""The Locator output schema — ranked suspects for where the bug lives.

Corresponds to "Schema 2: Locator Output Schema". The Locator agent returns
candidate files and functions, each with a confidence score in [0, 1], plus a
short reasoning string explaining the ranking.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CandidateFile(BaseModel):
    """A file the Locator believes may contain the bug."""

    file: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)


class CandidateFunction(BaseModel):
    """A function/class the Locator believes may contain the bug."""

    function: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)


class LocatorOutput(BaseModel):
    """Ranked localization results for a single bug."""

    bug_id: str = Field(..., min_length=1)
    candidate_files: list[CandidateFile] = Field(default_factory=list)
    candidate_functions: list[CandidateFunction] = Field(default_factory=list)
    reasoning: str = ""
