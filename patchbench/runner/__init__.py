"""Benchmark runner — loads bugs, drives the repair pipeline, watches for issues.

Provides:
- BenchmarkRunner: orchestrates evaluations across architectures
- IssueWatcher: monitors issues/pending/ for new submissions
- ApprovalGate: human-in-the-loop diff review
- Dataset loader utilities
"""

from patchbench.runner.loader import load_bug, load_all_bugs
from patchbench.runner.driver import BenchmarkRunner
from patchbench.runner.watcher import IssueWatcher
from patchbench.runner.approval import ApprovalGate

__all__ = ["load_bug", "load_all_bugs", "BenchmarkRunner", "IssueWatcher", "ApprovalGate"]
