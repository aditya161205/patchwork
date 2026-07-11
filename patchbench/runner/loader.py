"""Dataset loader — reads bug definitions from the benchmark directory."""

from __future__ import annotations

import json
from pathlib import Path

from patchbench.schemas import Bug
from patchbench.schemas.enums import BugType, Difficulty


def load_bug(bug_dir: str | Path) -> Bug:
    """Load a single Bug from a benchmark bug directory.

    Expects the directory to contain metadata.json and issue.md.
    """
    bug_dir = Path(bug_dir)
    metadata_path = bug_dir / "metadata.json"
    issue_path = bug_dir / "issue.md"

    if not metadata_path.exists():
        raise FileNotFoundError(f"metadata.json not found in {bug_dir}")

    with open(metadata_path) as f:
        meta = json.load(f)

    issue_text = ""
    if issue_path.exists():
        issue_text = issue_path.read_text(encoding="utf-8")

    return Bug(
        bug_id=meta["bug_id"],
        title=meta["title"],
        bug_type=BugType(meta["bug_type"]),
        difficulty=Difficulty(meta["difficulty"]),
        repo_path=meta["repo_path"],
        issue_description=issue_text,
        stack_trace=meta.get("stack_trace"),
        failing_tests=meta.get("failing_tests", []),
        expected_behavior=meta.get("expected_behavior", ""),
        actual_behavior=meta.get("actual_behavior", ""),
    )


def load_all_bugs(benchmark_dir: str | Path) -> list[Bug]:
    """Load all bugs from the benchmark/bugs/ directory."""
    benchmark_dir = Path(benchmark_dir)
    bugs_dir = benchmark_dir / "bugs"

    if not bugs_dir.is_dir():
        raise FileNotFoundError(f"Bugs directory not found: {bugs_dir}")

    bugs = []
    for bug_dir in sorted(bugs_dir.iterdir()):
        if bug_dir.is_dir() and (bug_dir / "metadata.json").exists():
            bugs.append(load_bug(bug_dir))
    return bugs
