"""Single-Agent Baseline — one-shot repair without localization or routing.

This baseline represents the simplest approach: read the entire bug context
and attempt a fix in a single pass with no specialized agents.
"""

from __future__ import annotations

import time

from patchbench.schemas import Bug, SingleAgentOutput, TestResults
from patchbench.schemas.enums import RunStatus
from patchbench.tools.file_read import read_file, list_files
from patchbench.tools.test_runner import run_tests
from patchbench.tools.patch_apply import apply_patch, revert_patch
from patchbench.tools.repo_search import grep_search


class SingleAgentBaseline:
    """Single-agent one-shot repair baseline.

    Strategy: scan files for keywords from bug title, read the most relevant
    file, apply simple heuristic fixes, and return the result.
    """

    def __init__(self, timeout: int = 60) -> None:
        self.timeout = timeout

    def run(self, bug: Bug, repo_path: str) -> SingleAgentOutput:
        """Execute a single-agent repair attempt."""
        start = time.time()

        # Run tests before
        before_result = run_tests(repo_path, bug.failing_tests, timeout=self.timeout)
        tests_before = TestResults(passed=before_result.passed, failed=before_result.failed)

        # Attempt repair
        patch = self._generate_patch(bug, repo_path)

        # Apply and test
        if patch:
            applied = apply_patch(repo_path, patch)
            if applied:
                after_result = run_tests(repo_path, timeout=self.timeout)
                tests_after = TestResults(passed=after_result.passed, failed=after_result.failed)
                revert_patch(repo_path, patch)
            else:
                tests_after = tests_before
        else:
            tests_after = tests_before

        runtime = time.time() - start
        status = RunStatus.SUCCESS if tests_after.failed == 0 else RunStatus.FAILURE

        return SingleAgentOutput(
            bug_id=bug.bug_id,
            patch=patch or "",
            tests_before=tests_before,
            tests_after=tests_after,
            runtime_seconds=round(runtime, 2),
            token_usage=0,
            status=status,
        )

    def _generate_patch(self, bug: Bug, repo_path: str) -> str | None:
        """Attempt to generate a fix using simple heuristics."""
        import difflib
        import re

        keywords = bug.title.lower().split()
        keywords = [w for w in keywords if len(w) > 3]

        best_file = None
        best_score = 0
        for f in list_files(repo_path, "**/*.py"):
            if "/tests/" in f or f.startswith("tests/"):
                continue
            score = 0
            try:
                content = read_file(repo_path, f)
            except (FileNotFoundError, UnicodeDecodeError):
                continue
            content_lower = content.lower()
            for kw in keywords:
                if kw in content_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_file = f

        if not best_file:
            return None

        content = read_file(repo_path, best_file)
        fixed = content

        # Simple operator fixes
        if "+" in content and ("percent" in bug.title.lower() or "discount" in bug.title.lower()):
            fixed = re.sub(r"(\w+)\s*\+\s*(\w+)\s*/\s*100", r"\1 * \2 / 100", fixed)

        if fixed == content:
            return None

        original_lines = content.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines, fixed_lines,
            fromfile=f"a/{best_file}", tofile=f"b/{best_file}",
        )
        return "".join(diff) or None
