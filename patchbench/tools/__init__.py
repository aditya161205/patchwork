"""Agent tools for interacting with bug repositories.

Provides file reading, searching, test running, patch application,
sandboxed execution, and cheat detection utilities.
"""

from patchbench.tools.file_read import read_file, list_files
from patchbench.tools.repo_search import grep_search, symbol_search
from patchbench.tools.test_runner import run_tests
from patchbench.tools.patch_apply import apply_patch, revert_patch
from patchbench.tools.linter import run_lint
from patchbench.tools.static_analysis import run_static_analysis
from patchbench.tools.sandbox import sandboxed_repo, run_in_sandbox
from patchbench.tools.cheat_detector import detect_cheats, is_clean
from patchbench.tools.verifier import verify_patch

__all__ = [
    "read_file",
    "list_files",
    "grep_search",
    "symbol_search",
    "run_tests",
    "apply_patch",
    "revert_patch",
    "run_lint",
    "run_static_analysis",
    "sandboxed_repo",
    "run_in_sandbox",
    "detect_cheats",
    "is_clean",
    "verify_patch",
]
