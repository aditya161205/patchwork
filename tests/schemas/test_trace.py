"""Tests for the Run Trace schema.

These focus on the one design decision that diverges from the doc's ``"..."``
placeholders: nested sub-models. We confirm that nested outputs are parsed into
their typed models, that a minimal/early-failure trace works, and that the whole
thing round-trips through JSON.
"""

from patchbench.schemas import (
    BugType,
    Complexity,
    FixerOutput,
    FixerType,
    JudgeOutput,
    LocatorOutput,
    RunStatus,
    RunTrace,
    ValidatorOutput,
)


def _full_trace_dict():
    return {
        "run_id": "RUN_001",
        "bug_id": "BUG_001",
        "bug_type": "logical_error",
        "complexity": "complex",
        "selected_fixer": "LogicFixer",
        "tool_calls": 12,
        "subagents_spawned": 2,
        "locator_output": {
            "bug_id": "BUG_001",
            "candidate_files": [{"file": "src/cart.py", "confidence": 0.92}],
            "reasoning": "test invokes calculate_total",
        },
        "fixer_output": {
            "bug_id": "BUG_001",
            "fixer_type": "LogicFixer",
            "files_modified": ["src/cart.py"],
            "patch": "diff",
            "confidence": 0.88,
            "root_cause": "sign reversed",
            "explanation": "fixed",
        },
        "validator_output": {
            "bug_id": "BUG_001",
            "validation_status": "PASS",
            "tests_before": {"passed": 18, "failed": 1},
            "tests_after": {"passed": 19, "failed": 0},
            "lint_status": "PASS",
            "static_analysis_status": "PASS",
            "validation_report": "ok",
        },
        "judge_output": {
            "bug_id": "BUG_001",
            "fix_rate": 1,
            "runtime_seconds": 42,
            "token_usage": 12450,
            "files_modified": 1,
            "patch_size_lines": 4,
            "regressions": 0,
            "judge_score": 9.1,
            "status": "SUCCESS",
        },
        "final_status": "SUCCESS",
    }


def test_nested_outputs_parse_into_typed_submodels():
    trace = RunTrace(**_full_trace_dict())
    assert trace.bug_type is BugType.LOGICAL_ERROR
    assert trace.complexity is Complexity.COMPLEX
    assert trace.selected_fixer is FixerType.LOGIC_FIXER
    assert isinstance(trace.locator_output, LocatorOutput)
    assert isinstance(trace.fixer_output, FixerOutput)
    assert isinstance(trace.validator_output, ValidatorOutput)
    assert isinstance(trace.judge_output, JudgeOutput)
    assert trace.final_status is RunStatus.SUCCESS


def test_minimal_trace_allows_missing_stage_outputs():
    # An early-failure trace, persisted before any agent stage completed.
    trace = RunTrace(
        run_id="RUN_002",
        bug_id="BUG_004",
        bug_type="syntax_error",
        complexity="simple",
        selected_fixer="SyntaxFixer",
        final_status="FAILURE",
    )
    assert trace.locator_output is None
    assert trace.fixer_output is None
    assert trace.tool_calls == 0
    assert trace.subagents_spawned == 0


def test_round_trip_json():
    trace = RunTrace(**_full_trace_dict())
    assert RunTrace.model_validate_json(trace.model_dump_json()) == trace
