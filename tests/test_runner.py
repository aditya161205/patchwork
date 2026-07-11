"""Tests for the runner package."""

import os

from patchbench.runner import load_bug, load_all_bugs

BENCHMARK_DIR = os.path.join(os.path.dirname(__file__), "..", "benchmark")


def test_load_single_bug():
    bug = load_bug(os.path.join(BENCHMARK_DIR, "bugs", "BUG_001"))
    assert bug.bug_id == "BUG_001"
    assert bug.title == "Percentage coupons produce incorrect order totals"
    assert len(bug.failing_tests) > 0


def test_load_all_bugs():
    bugs = load_all_bugs(BENCHMARK_DIR)
    assert len(bugs) == 20
    bug_ids = [b.bug_id for b in bugs]
    assert "BUG_001" in bug_ids
    assert "BUG_020" in bug_ids


def test_all_bugs_have_required_fields():
    bugs = load_all_bugs(BENCHMARK_DIR)
    for bug in bugs:
        assert bug.bug_id
        assert bug.title
        assert bug.bug_type
        assert bug.difficulty
        assert bug.repo_path
        assert len(bug.failing_tests) > 0
