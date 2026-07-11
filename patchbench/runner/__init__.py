"""Benchmark runner — loads bugs and drives the repair pipeline.

Provides the BenchmarkRunner that orchestrates full evaluation runs
across the bug dataset with configurable agent architectures.
"""

from patchbench.runner.loader import load_bug, load_all_bugs
from patchbench.runner.driver import BenchmarkRunner

__all__ = ["load_bug", "load_all_bugs", "BenchmarkRunner"]
