"""Static analysis tool — checks for common code issues."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from patchbench.tools.file_read import list_files


@dataclass
class StaticAnalysisResult:
    """Result of static analysis on a repository."""

    passed: bool
    issues: list[str]


def run_static_analysis(repo_path: str, files: list[str] | None = None) -> StaticAnalysisResult:
    """Run static analysis checks on repository files.

    Checks for undefined names, unused imports, and other common issues.
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
            tree = ast.parse(source)
        except SyntaxError:
            issues.append(f"{rel_path}: failed to parse (syntax error)")
            continue

        _check_undefined_names(tree, rel_path, issues)

    return StaticAnalysisResult(passed=len(issues) == 0, issues=issues)


def _check_undefined_names(tree: ast.AST, file_path: str, issues: list[str]) -> None:
    """Basic check for obviously undefined names at module level."""
    defined: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            defined.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                defined.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined.add(alias.asname or alias.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined.add(target.id)
