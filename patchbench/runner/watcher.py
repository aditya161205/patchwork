"""Filesystem watcher — monitors issues/pending/ for new bug submissions.

Watches a directory for new .json files representing bug submissions.
When a new file appears, it is loaded and queued for processing.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from patchbench.schemas import Bug
from patchbench.runner.loader import load_bug


class IssueWatcher:
    """Watches a directory for new issue submissions.

    Expected directory structure:
        issues/
            pending/    <- new issues land here (as directories with metadata.json)
            processing/ <- issues currently being fixed
            resolved/   <- successfully fixed issues
            failed/     <- issues that could not be resolved

    Each issue directory should contain metadata.json + issue.md (same format
    as benchmark/bugs/BUG_XXX/).
    """

    def __init__(self, watch_dir: str | Path, poll_interval: float = 2.0) -> None:
        self.watch_dir = Path(watch_dir)
        self.pending_dir = self.watch_dir / "pending"
        self.processing_dir = self.watch_dir / "processing"
        self.resolved_dir = self.watch_dir / "resolved"
        self.failed_dir = self.watch_dir / "failed"
        self.poll_interval = poll_interval
        self._running = False

    def setup(self) -> None:
        """Create the watch directory structure if it doesn't exist."""
        for d in (self.pending_dir, self.processing_dir, self.resolved_dir, self.failed_dir):
            d.mkdir(parents=True, exist_ok=True)

    def scan_pending(self) -> list[Path]:
        """Return list of pending issue directories (non-destructive scan)."""
        if not self.pending_dir.exists():
            return []
        return sorted(
            d for d in self.pending_dir.iterdir()
            if d.is_dir() and (d / "metadata.json").exists()
        )

    def claim_issue(self, issue_dir: Path) -> Path | None:
        """Move an issue from pending to processing. Returns new path or None."""
        dest = self.processing_dir / issue_dir.name
        if dest.exists():
            return None
        try:
            issue_dir.rename(dest)
            return dest
        except OSError:
            return None

    def mark_resolved(self, issue_dir: Path) -> Path:
        """Move a processed issue to resolved."""
        dest = self.resolved_dir / issue_dir.name
        issue_dir.rename(dest)
        return dest

    def mark_failed(self, issue_dir: Path) -> Path:
        """Move a processed issue to failed."""
        dest = self.failed_dir / issue_dir.name
        issue_dir.rename(dest)
        return dest

    def watch(self, callback: Callable[[Bug, Path], bool], max_iterations: int | None = None) -> None:
        """Poll for new issues and process them via callback.

        Args:
            callback: Called with (Bug, issue_dir_path). Return True if resolved.
            max_iterations: If set, stop after this many polls (for testing).
        """
        self.setup()
        self._running = True
        iterations = 0

        while self._running:
            pending = self.scan_pending()
            for issue_dir in pending:
                claimed = self.claim_issue(issue_dir)
                if claimed is None:
                    continue

                try:
                    bug = load_bug(claimed)
                    resolved = callback(bug, claimed)
                    if resolved:
                        self.mark_resolved(claimed)
                    else:
                        self.mark_failed(claimed)
                except Exception:
                    self.mark_failed(claimed)

            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break

            time.sleep(self.poll_interval)

    def stop(self) -> None:
        """Signal the watcher to stop."""
        self._running = False
