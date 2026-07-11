"""Repository search tools: grep and symbol lookup."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from patchbench.tools.file_read import list_files, read_file


@dataclass
class SearchHit:
    """A single search result."""

    file: str
    line: int
    text: str


def grep_search(repo_path: str, pattern: str, file_glob: str = "**/*.py") -> list[SearchHit]:
    """Search for a regex pattern across repository files."""
    regex = re.compile(pattern)
    hits: list[SearchHit] = []
    for rel_path in list_files(repo_path, file_glob):
        try:
            content = read_file(repo_path, rel_path)
        except (FileNotFoundError, UnicodeDecodeError):
            continue
        for i, line in enumerate(content.splitlines(), 1):
            if regex.search(line):
                hits.append(SearchHit(file=rel_path, line=i, text=line.strip()))
    return hits


@dataclass
class SymbolInfo:
    """Information about a code symbol (function/class)."""

    name: str
    kind: str  # "function", "class", "method"
    file: str
    line: int


def symbol_search(repo_path: str, name: str | None = None) -> list[SymbolInfo]:
    """Find function and class definitions in the repository.

    If name is provided, filters to symbols matching that name (substring match).
    """
    symbols: list[SymbolInfo] = []
    for rel_path in list_files(repo_path, "**/*.py"):
        try:
            content = read_file(repo_path, rel_path)
            tree = ast.parse(content)
        except (FileNotFoundError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                kind = "function"
                sym_name = node.name
            elif isinstance(node, ast.ClassDef):
                kind = "class"
                sym_name = node.name
            else:
                continue
            if name is None or name.lower() in sym_name.lower():
                symbols.append(SymbolInfo(
                    name=sym_name, kind=kind, file=rel_path, line=node.lineno
                ))
    return symbols
