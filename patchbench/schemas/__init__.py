"""PatchBench data contracts.

Every agent in the pipeline communicates through these typed schemas. Import
them from this package rather than the individual modules, e.g.::

    from patchbench.schemas import Bug, LocatorOutput, RunTrace
"""

from patchbench.schemas.baseline import SingleAgentOutput
from patchbench.schemas.bug import Bug
from patchbench.schemas.enums import (
    BugType,
    CheckStatus,
    Complexity,
    Difficulty,
    FixerType,
    RunStatus,
)
from patchbench.schemas.fixer import FixerOutput
from patchbench.schemas.judge import JudgeOutput
from patchbench.schemas.locator import CandidateFile, CandidateFunction, LocatorOutput
from patchbench.schemas.trace import RunTrace
from patchbench.schemas.validator import TestResults, ValidatorOutput

__all__ = [
    # enums
    "BugType",
    "Difficulty",
    "Complexity",
    "FixerType",
    "CheckStatus",
    "RunStatus",
    # core schemas
    "Bug",
    "CandidateFile",
    "CandidateFunction",
    "LocatorOutput",
    "FixerOutput",
    "TestResults",
    "ValidatorOutput",
    "JudgeOutput",
    "RunTrace",
    "SingleAgentOutput",
]
