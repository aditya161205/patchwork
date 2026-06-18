"""Shared enumerations used across PatchBench schemas.

These replace free-text strings (e.g. ``"logical_error"``, ``"LogicFixer"``,
``"PASS"``) with closed vocabularies so that every agent in the pipeline agrees
on the exact set of allowed values. Each enum inherits from ``str`` so the
members serialize to their plain string value in JSON (matching the design doc
exactly) while still being type-checked in code.
"""

from enum import Enum


class BugType(str, Enum):
    """The seven bug categories the Orchestrator classifies bugs into."""

    SYNTAX_ERROR = "syntax_error"
    LOGICAL_ERROR = "logical_error"
    API_MISMATCH = "api_mismatch"
    STATE_BUG = "state_bug"
    TEST_FAILURE = "test_failure"
    DEPENDENCY_CONFIG_BUG = "dependency_config_bug"
    PERFORMANCE_BUG = "performance_bug"


class Difficulty(str, Enum):
    """Benchmark difficulty tier of a bug task."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Complexity(str, Enum):
    """Orchestrator's estimate of task complexity, used for budgeting."""

    SIMPLE = "simple"
    COMPLEX = "complex"


class FixerType(str, Enum):
    """The specialized Fixer agents a bug can be routed to.

    One Fixer maps to each repair-relevant bug category. ``ConfigFixer`` covers
    both configuration and dependency bugs (the "Config/Dependency Fixer").
    """

    SYNTAX_FIXER = "SyntaxFixer"
    LOGIC_FIXER = "LogicFixer"
    API_FIXER = "APIFixer"
    STATE_FIXER = "StateFixer"
    CONFIG_FIXER = "ConfigFixer"
    PERFORMANCE_FIXER = "PerformanceFixer"


class CheckStatus(str, Enum):
    """Binary PASS/FAIL outcome of a validation check.

    Shared by the Validator's overall verdict as well as its lint and
    static-analysis sub-checks.
    """

    PASS = "PASS"
    FAIL = "FAIL"


class RunStatus(str, Enum):
    """Terminal status of a repair attempt / benchmark run."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
