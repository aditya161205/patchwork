"""Tests for the shared enums.

The key guarantees we lock in: every category from the design doc is present,
and each member serializes to the exact lowercase/CamelCase string the doc uses
(because the rest of the system and any stored JSON depend on those values).
"""

from patchbench.schemas.enums import (
    BugType,
    CheckStatus,
    Complexity,
    Difficulty,
    FixerType,
    RunStatus,
)


def test_bug_type_values_match_doc():
    assert {b.value for b in BugType} == {
        "syntax_error",
        "logical_error",
        "api_mismatch",
        "state_bug",
        "test_failure",
        "dependency_config_bug",
        "performance_bug",
    }


def test_fixer_type_values_match_doc():
    assert {f.value for f in FixerType} == {
        "SyntaxFixer",
        "LogicFixer",
        "APIFixer",
        "StateFixer",
        "ConfigFixer",
        "PerformanceFixer",
    }


def test_simple_enum_value_sets():
    assert {d.value for d in Difficulty} == {"easy", "medium", "hard"}
    assert {c.value for c in Complexity} == {"simple", "complex"}
    assert {s.value for s in CheckStatus} == {"PASS", "FAIL"}
    assert {s.value for s in RunStatus} == {"SUCCESS", "FAILURE"}


def test_enums_are_str_subclasses():
    # str mixin is what makes them serialize as plain strings in JSON.
    assert isinstance(BugType.LOGICAL_ERROR, str)
    assert BugType.LOGICAL_ERROR == "logical_error"
