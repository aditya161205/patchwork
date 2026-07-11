"""Tests for the filesystem watcher."""

import json
import os
import tempfile
from pathlib import Path

from patchbench.runner.watcher import IssueWatcher
from patchbench.schemas import Bug


def _create_issue(issue_dir: Path, bug_id: str = "TEST_001") -> None:
    """Create a minimal issue directory."""
    issue_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "bug_id": bug_id,
        "title": "Test bug",
        "bug_type": "logical_error",
        "difficulty": "easy",
        "difficulty_score": 1,
        "repo_path": "benchmark/bugs/BUG_001/repo",
        "issue_file": "issue.md",
        "failing_tests": ["tests/test_discount.py::test_percentage_discount"],
    }
    (issue_dir / "metadata.json").write_text(json.dumps(metadata))
    (issue_dir / "issue.md").write_text("Test issue\n")


def test_watcher_setup_creates_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        watcher = IssueWatcher(tmp)
        watcher.setup()
        assert (Path(tmp) / "pending").is_dir()
        assert (Path(tmp) / "processing").is_dir()
        assert (Path(tmp) / "resolved").is_dir()
        assert (Path(tmp) / "failed").is_dir()


def test_watcher_scan_pending():
    with tempfile.TemporaryDirectory() as tmp:
        watcher = IssueWatcher(tmp)
        watcher.setup()
        # Empty initially
        assert watcher.scan_pending() == []
        # Add an issue
        _create_issue(Path(tmp) / "pending" / "ISSUE_001")
        pending = watcher.scan_pending()
        assert len(pending) == 1
        assert pending[0].name == "ISSUE_001"


def test_watcher_claim_issue():
    with tempfile.TemporaryDirectory() as tmp:
        watcher = IssueWatcher(tmp)
        watcher.setup()
        _create_issue(Path(tmp) / "pending" / "ISSUE_001")
        pending = watcher.scan_pending()
        claimed = watcher.claim_issue(pending[0])
        assert claimed is not None
        assert claimed.parent.name == "processing"
        assert not (Path(tmp) / "pending" / "ISSUE_001").exists()


def test_watcher_mark_resolved():
    with tempfile.TemporaryDirectory() as tmp:
        watcher = IssueWatcher(tmp)
        watcher.setup()
        _create_issue(Path(tmp) / "pending" / "ISSUE_001")
        claimed = watcher.claim_issue(watcher.scan_pending()[0])
        resolved = watcher.mark_resolved(claimed)
        assert resolved.parent.name == "resolved"


def test_watcher_watch_callback():
    with tempfile.TemporaryDirectory() as tmp:
        watcher = IssueWatcher(tmp, poll_interval=0.1)
        watcher.setup()
        _create_issue(Path(tmp) / "pending" / "ISSUE_001")

        processed = []

        def callback(bug: Bug, path: Path) -> bool:
            processed.append(bug.bug_id)
            return True  # resolved

        watcher.watch(callback, max_iterations=1)
        assert "TEST_001" in processed
        assert (Path(tmp) / "resolved" / "ISSUE_001").is_dir()


def test_watcher_failed_callback():
    with tempfile.TemporaryDirectory() as tmp:
        watcher = IssueWatcher(tmp, poll_interval=0.1)
        watcher.setup()
        _create_issue(Path(tmp) / "pending" / "ISSUE_002")

        def callback(bug: Bug, path: Path) -> bool:
            return False  # failed

        watcher.watch(callback, max_iterations=1)
        assert (Path(tmp) / "failed" / "ISSUE_002").is_dir()
