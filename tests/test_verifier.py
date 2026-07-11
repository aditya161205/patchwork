"""Tests for the verifier backbone.

Verifies:
- Reference patch resolves the bug (PASS verdict)
- Empty patch fails (FAIL verdict)
- Test-file-editing patch is flagged as CHEATED
"""

import os

import pytest

from patchbench.tools.verifier import verify_patch
from patchbench.tools.cheat_detector import detect_cheats, is_clean

BENCHMARK_DIR = os.path.join(os.path.dirname(__file__), "..", "benchmark")
BUG_001_REPO = os.path.join(BENCHMARK_DIR, "bugs", "BUG_001", "repo")
BUG_001_FAILING = [
    "tests/test_discount.py::test_percentage_discount",
    "tests/test_coupon.py::test_percent_coupon_discount",
    "tests/test_checkout.py::test_summary_with_coupon",
]

REFERENCE_PATCH = """\
--- a/ecommerce/discount.py
+++ b/ecommerce/discount.py
@@ -10,7 +10,7 @@
     require_non_negative(amount, "amount")
     if not 0 <= percent <= 100:
         raise ValueError(f"percent must be between 0 and 100, got {percent}")
-    return round_money(amount + percent / 100)
+    return round_money(amount * percent / 100)


 def fixed_discount(amount: float, value: float) -> float:
"""


def test_reference_patch_resolves():
    """The reference patch should get a PASS verdict."""
    result = verify_patch(
        repo_path=BUG_001_REPO,
        patch=REFERENCE_PATCH,
        failing_tests=BUG_001_FAILING,
        timeout=30,
    )
    assert result.verdict == "PASS"
    assert result.patch_applied is True
    assert result.fail_to_pass_resolved > 0
    assert result.regressions == 0
    assert result.is_clean is True


def test_empty_patch_fails():
    """An empty patch should get a FAIL verdict."""
    result = verify_patch(
        repo_path=BUG_001_REPO,
        patch="",
        failing_tests=BUG_001_FAILING,
        timeout=30,
    )
    assert result.verdict == "FAIL"
    assert result.patch_applied is False


def test_test_file_edit_flagged():
    """A patch that modifies test files should be flagged as CHEATED."""
    cheating_patch = """\
--- a/tests/test_discount.py
+++ b/tests/test_discount.py
@@ -5,7 +5,7 @@


 def test_percentage_discount():
-    assert percentage_discount(200.0, 10) == 20.0
+    assert True
"""
    result = verify_patch(
        repo_path=BUG_001_REPO,
        patch=cheating_patch,
        failing_tests=BUG_001_FAILING,
        timeout=30,
    )
    assert result.verdict == "CHEATED"
    assert not result.is_clean
    assert any(f.rule == "test_file_edit" for f in result.cheat_flags)


def test_cheat_detector_test_file_edit():
    """Cheat detector catches test file modifications."""
    patch = "+++ b/tests/test_foo.py\n+assert True\n"
    flags = detect_cheats(patch)
    assert any(f.rule == "test_file_edit" for f in flags)


def test_cheat_detector_clean_patch():
    """Clean source-only patches pass cheat detection."""
    assert is_clean(REFERENCE_PATCH, BUG_001_FAILING)


def test_cheat_detector_test_deletion():
    """Cheat detector catches deletion of failing test functions."""
    patch = "--- a/tests/test_discount.py\n-def test_percentage_discount():\n"
    flags = detect_cheats(patch, ["tests/test_discount.py::test_percentage_discount"])
    assert any(f.rule == "test_deletion" for f in flags)


def test_cheat_detector_noop_assertion():
    """Cheat detector catches 'assert True' insertions."""
    patch = "+++ b/ecommerce/discount.py\n+    assert True\n"
    flags = detect_cheats(patch)
    assert any(f.rule == "noop_assertion" for f in flags)
