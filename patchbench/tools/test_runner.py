"""Test runner tool — executes pytest on a repository and returns results."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestRunResult:
    """Result of running a test suite."""

    passed: int
    failed: int
    errors: int
    output: str
    returncode: int

    @property
    def all_passed(self) -> bool:
        return self.failed == 0 and self.errors == 0


def run_tests(
    repo_path: str,
    test_files: list[str] | None = None,
    timeout: int = 60,
) -> TestRunResult:
    """Run pytest on a repository and parse the results.

    Args:
        repo_path: Path to the repository root.
        test_files: Optional list of specific test files/ids to run.
        timeout: Maximum seconds before killing the test process.
    """
    repo = Path(repo_path)
    if not repo.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    cmd = [sys.executable, "-m", "pytest", "--tb=short", "-q"]
    if test_files:
        cmd.extend(test_files)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return TestRunResult(passed=0, failed=0, errors=1, output="TIMEOUT", returncode=-1)

    output = result.stdout + result.stderr
    passed, failed, errors = _parse_pytest_output(output)
    return TestRunResult(
        passed=passed,
        failed=failed,
        errors=errors,
        output=output,
        returncode=result.returncode,
    )


def _parse_pytest_output(output: str) -> tuple[int, int, int]:
    """Extract pass/fail/error counts from pytest output."""
    import re

    passed = failed = errors = 0
    for line in output.splitlines():
        m = re.search(r"(\d+) passed", line)
        if m:
            passed = int(m.group(1))
        m = re.search(r"(\d+) failed", line)
        if m:
            failed = int(m.group(1))
        m = re.search(r"(\d+) error", line)
        if m:
            errors = int(m.group(1))
    return passed, failed, errors
