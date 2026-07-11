"""File reading and listing tools for agents."""

from __future__ import annotations

import os
from pathlib import Path


def read_file(repo_path: str, file_path: str) -> str:
    """Read the contents of a file within a repository.

    Returns the file contents as a string, or raises FileNotFoundError.
    """
    full_path = Path(repo_path) / file_path
    if not full_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    return full_path.read_text(encoding="utf-8")


def list_files(repo_path: str, pattern: str = "**/*.py") -> list[str]:
    """List files in a repository matching a glob pattern.

    Returns paths relative to repo_path.
    """
    root = Path(repo_path)
    if not root.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")
    results = []
    for p in sorted(root.glob(pattern)):
        if p.is_file():
            rel = str(p.relative_to(root))
            if not any(part.startswith(".") for part in rel.split(os.sep)):
                results.append(rel)
    return results
