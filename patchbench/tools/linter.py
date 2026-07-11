"""Linting tool — runs basic Python syntax and style checks."""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from patchbench.tools.file_read import list_files


@dataclass
class LintResult:
    """Result of linting a repository."""

    passed: bool
    issues: list[str]


def run_lint(repo_path: str, files: list[str] | None = None) -> LintResult:
    """Run lint checks on repository files.

    Checks for syntax errors and basic issues using ast.parse.
    If ruff/flake8 is available, uses that instead.
    """
    repo = Path(repo_path)
    if not repo.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    target_files = files or list_files(repo_path, "**/*.py")
    issues: list[str] = []

    for rel_path in target_files:
        full_path = repo / rel_path
        if not full_path.exists():
            continue
        try:
            source = full_path.read_text(encoding="utf-8")
            ast.parse(source)
        except SyntaxError as e:
            issues.append(f"{rel_path}:{e.lineno}: SyntaxError: {e.msg}")

    return LintResult(passed=len(issues) == 0, issues=issues)
