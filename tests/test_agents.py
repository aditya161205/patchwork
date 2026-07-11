"""Tests for the agents package."""

import os

from patchbench.schemas import Bug
from patchbench.schemas.enums import BugType, Complexity, Difficulty, FixerType
from patchbench.agents import Orchestrator, Locator
from patchbench.runner import load_bug

BENCHMARK_DIR = os.path.join(os.path.dirname(__file__), "..", "benchmark")


def _bug(bug_type=BugType.LOGICAL_ERROR, difficulty=Difficulty.MEDIUM, failing_tests=None):
    return Bug(
        bug_id="TEST_001",
        title="Test bug",
        bug_type=bug_type,
        difficulty=difficulty,
        repo_path="benchmark/repos/ecommerce",
        issue_description="Test issue",
        failing_tests=failing_tests or ["tests/test_cart.py::test_add_item_and_subtotal"],
        expected_behavior="works",
        actual_behavior="broken",
    )


def test_orchestrator_classify():
    orch = Orchestrator()
    bug_type, complexity = orch.classify(_bug())
    assert bug_type == BugType.LOGICAL_ERROR
    assert complexity == Complexity.SIMPLE


def test_orchestrator_classify_hard_is_complex():
    orch = Orchestrator()
    _, complexity = orch.classify(_bug(difficulty=Difficulty.HARD))
    assert complexity == Complexity.COMPLEX


def test_orchestrator_routes_correctly():
    orch = Orchestrator()
    assert orch.select_fixer(BugType.LOGICAL_ERROR) == FixerType.LOGIC_FIXER
    assert orch.select_fixer(BugType.SYNTAX_ERROR) == FixerType.SYNTAX_FIXER
    assert orch.select_fixer(BugType.API_MISMATCH) == FixerType.API_FIXER
    assert orch.select_fixer(BugType.STATE_BUG) == FixerType.STATE_FIXER
    assert orch.select_fixer(BugType.DEPENDENCY_CONFIG_BUG) == FixerType.CONFIG_FIXER
    assert orch.select_fixer(BugType.PERFORMANCE_BUG) == FixerType.PERFORMANCE_FIXER


def test_locator_finds_files():
    bug = load_bug(os.path.join(BENCHMARK_DIR, "bugs", "BUG_006"))
    locator = Locator()
    result = locator.locate(bug, os.path.join(BENCHMARK_DIR, "bugs", "BUG_006", "repo"))
    files = [f.file for f in result.candidate_files]
    assert "ecommerce/tax.py" in files


def test_locator_returns_valid_schema():
    bug = load_bug(os.path.join(BENCHMARK_DIR, "bugs", "BUG_001"))
    locator = Locator()
    result = locator.locate(bug, os.path.join(BENCHMARK_DIR, "bugs", "BUG_001", "repo"))
    assert result.bug_id == "BUG_001"
    assert len(result.reasoning) > 0
