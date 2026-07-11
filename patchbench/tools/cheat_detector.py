"""Cheat detection — flags patches that game the benchmark rather than fix bugs.

Detectors:
1. Test-file edits: patch modifies test files (makes tests pass by changing expectations)
2. Hardcoded outputs: patch inserts literal return values that match test assertions
3. Delete-to-pass: patch deletes the failing test entirely
4. Noop assertions: patch replaces assertions with pass/True
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CheatFlag:
    """A single cheat detection flag."""

    rule: str
    severity: str  # "critical", "warning"
    description: str
    evidence: str


def detect_cheats(patch: str, failing_tests: list[str] | None = None) -> list[CheatFlag]:
    """Run all cheat detectors on a patch. Returns list of flags (empty = clean)."""
    flags: list[CheatFlag] = []
    flags.extend(_detect_test_file_edits(patch))
    flags.extend(_detect_hardcoded_outputs(patch))
    flags.extend(_detect_test_deletion(patch, failing_tests))
    flags.extend(_detect_noop_assertions(patch))
    return flags


def _detect_test_file_edits(patch: str) -> list[CheatFlag]:
    """Flag patches that modify test files."""
    flags = []
    modified_files = re.findall(r"^\+\+\+ [ab]/(.+)$", patch, re.MULTILINE)
    for f in modified_files:
        if "/tests/" in f or f.startswith("tests/") or "/test_" in f or f.startswith("test_"):
            flags.append(CheatFlag(
                rule="test_file_edit",
                severity="critical",
                description=f"Patch modifies test file: {f}",
                evidence=f,
            ))
    return flags


def _detect_hardcoded_outputs(patch: str) -> list[CheatFlag]:
    """Flag patches that insert suspiciously hardcoded return values."""
    flags = []
    added_lines = [line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++")]

    for line in added_lines:
        stripped = line.strip()
        # Detect: return <literal> where the literal matches common test values
        if re.match(r"return\s+([\d.]+|True|False|None|\[\]|\{\}|\"[^\"]*\"|'[^']*')$", stripped):
            # Check if this is inside a function that previously did computation
            if not any(kw in stripped for kw in ("return self.", "return cls.")):
                flags.append(CheatFlag(
                    rule="hardcoded_output",
                    severity="warning",
                    description="Patch inserts a literal return value",
                    evidence=stripped,
                ))

    return flags


def _detect_test_deletion(patch: str, failing_tests: list[str] | None) -> list[CheatFlag]:
    """Flag patches that delete test functions entirely."""
    flags = []
    if not failing_tests:
        return flags

    removed_lines = [line[1:] for line in patch.splitlines() if line.startswith("-") and not line.startswith("---")]

    test_func_names = set()
    for test_id in failing_tests:
        if "::" in test_id:
            test_func_names.add(test_id.split("::")[-1])

    for line in removed_lines:
        stripped = line.strip()
        if stripped.startswith("def "):
            func_name = stripped.split("(")[0].replace("def ", "")
            if func_name in test_func_names:
                flags.append(CheatFlag(
                    rule="test_deletion",
                    severity="critical",
                    description=f"Patch deletes failing test function: {func_name}",
                    evidence=stripped,
                ))

    return flags


def _detect_noop_assertions(patch: str) -> list[CheatFlag]:
    """Flag patches that replace assertions with pass or always-true."""
    flags = []
    added_lines = [line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++")]

    for line in added_lines:
        stripped = line.strip()
        if stripped == "assert True":
            flags.append(CheatFlag(
                rule="noop_assertion",
                severity="critical",
                description="Patch inserts 'assert True' (noop assertion)",
                evidence=stripped,
            ))
        if stripped == "pass" and "# " not in stripped:
            # Check context — removing a test body and replacing with pass
            pass  # This needs more context to be reliable, skip for now

    return flags


def is_clean(patch: str, failing_tests: list[str] | None = None) -> bool:
    """Return True if patch passes all cheat checks (no critical flags)."""
    flags = detect_cheats(patch, failing_tests)
    return not any(f.severity == "critical" for f in flags)
