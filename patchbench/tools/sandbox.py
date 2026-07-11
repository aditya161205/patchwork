"""Sandbox execution — copy repo to temp dir, apply patch, run tests safely."""

from __future__ import annotations

import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

from patchbench.tools.patch_apply import apply_patch
from patchbench.tools.test_runner import run_tests, TestRunResult
from patchbench.tools.linter import run_lint, LintResult
from patchbench.tools.static_analysis import run_static_analysis, StaticAnalysisResult


@dataclass
class SandboxResult:
    """Complete result from a sandboxed patch evaluation."""

    patch_applied: bool
    tests_before: TestRunResult
    tests_after: TestRunResult
    lint: LintResult
    static_analysis: StaticAnalysisResult
    sandbox_path: str


@contextmanager
def sandboxed_repo(repo_path: str) -> Generator[str, None, None]:
    """Copy a repository to a temporary directory for safe mutation.

    The temp directory is automatically cleaned up on exit, even if an
    exception occurs. This protects the original repo from corruption
    during patch application or test runs.
    """
    repo = Path(repo_path)
    if not repo.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    tmp_dir = tempfile.mkdtemp(prefix="patchbench_sandbox_")
    sandbox_path = Path(tmp_dir) / "repo"
    try:
        shutil.copytree(repo, sandbox_path)
        # Remove __pycache__ to prevent stale bytecode from masking bugs
        for cache_dir in sandbox_path.rglob("__pycache__"):
            shutil.rmtree(cache_dir)
        yield str(sandbox_path)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def run_in_sandbox(
    repo_path: str,
    patch: str,
    failing_tests: list[str] | None = None,
    timeout: int = 60,
) -> SandboxResult:
    """Apply a patch in an isolated sandbox and run full verification.

    1. Copies repo to a temp directory
    2. Runs tests BEFORE patch (on buggy code) to get baseline
    3. Applies the patch
    4. Runs tests AFTER patch
    5. Runs lint and static analysis
    6. Cleans up temp directory

    The original repo is NEVER modified.
    """
    with sandboxed_repo(repo_path) as sandbox_path:
        # Tests before (on buggy code)
        tests_before = run_tests(sandbox_path, failing_tests, timeout=timeout)

        # Apply patch
        patch_applied = False
        if patch:
            patch_applied = apply_patch(sandbox_path, patch)

        # Tests after
        if patch_applied:
            tests_after = run_tests(sandbox_path, timeout=timeout)
        else:
            tests_after = tests_before

        # Lint and static analysis
        lint = run_lint(sandbox_path)
        sa = run_static_analysis(sandbox_path)

        return SandboxResult(
            patch_applied=patch_applied,
            tests_before=tests_before,
            tests_after=tests_after,
            lint=lint,
            static_analysis=sa,
            sandbox_path=sandbox_path,
        )
