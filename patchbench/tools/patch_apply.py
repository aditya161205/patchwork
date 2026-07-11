"""Patch application and reversion tools."""

from __future__ import annotations

import subprocess
from pathlib import Path


def apply_patch(repo_path: str, patch: str) -> bool:
    """Apply a unified diff patch to a repository.

    Returns True if the patch applied cleanly, False otherwise.
    """
    repo = Path(repo_path)
    if not repo.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    result = subprocess.run(
        ["patch", "-p1", "--forward"],
        input=patch,
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def revert_patch(repo_path: str, patch: str) -> bool:
    """Reverse-apply a unified diff patch.

    Returns True if the reversion succeeded, False otherwise.
    """
    repo = Path(repo_path)
    if not repo.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    result = subprocess.run(
        ["patch", "-p1", "--reverse"],
        input=patch,
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    return result.returncode == 0
