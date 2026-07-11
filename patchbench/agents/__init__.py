"""Multi-agent pipeline: Orchestrator, Locator, Fixers, Validator, Judge.

Each agent is a callable class that takes typed input and returns typed output
matching the schemas defined in patchbench.schemas.
"""

from patchbench.agents.orchestrator import Orchestrator
from patchbench.agents.locator import Locator
from patchbench.agents.fixer import (
    BaseFixer,
    SyntaxFixer,
    LogicFixer,
    APIFixer,
    StateFixer,
    ConfigFixer,
    PerformanceFixer,
    get_fixer,
)
from patchbench.agents.validator import Validator
from patchbench.agents.judge import Judge

__all__ = [
    "Orchestrator",
    "Locator",
    "BaseFixer",
    "SyntaxFixer",
    "LogicFixer",
    "APIFixer",
    "StateFixer",
    "ConfigFixer",
    "PerformanceFixer",
    "get_fixer",
    "Validator",
    "Judge",
]
