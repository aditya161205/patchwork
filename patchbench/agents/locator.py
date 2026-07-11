"""Locator agent — finds candidate files and functions containing the bug."""

from __future__ import annotations

from pathlib import Path

from patchbench.schemas import Bug, CandidateFile, CandidateFunction, LocatorOutput
from patchbench.tools.repo_search import grep_search, symbol_search
from patchbench.tools.file_read import list_files


class Locator:
    """Locates likely bug locations using search heuristics.

    Strategy:
    1. Search for keywords from the issue description and failing test names
    2. Search for relevant symbols (functions/classes)
    3. Rank candidates by hit frequency and relevance
    """

    def locate(self, bug: Bug, repo_path: str) -> LocatorOutput:
        """Identify candidate files and functions for the bug."""
        file_scores: dict[str, float] = {}
        function_scores: dict[str, float] = {}

        keywords = self._extract_keywords(bug)

        for keyword in keywords:
            hits = grep_search(repo_path, keyword)
            for hit in hits:
                if self._is_test_file(hit.file):
                    continue
                file_scores[hit.file] = file_scores.get(hit.file, 0) + 1.0

        for test_id in bug.failing_tests:
            test_file = test_id.split("::")[0]
            test_name = test_id.split("::")[-1] if "::" in test_id else ""
            module_hint = self._test_to_source_hint(test_file)
            if module_hint:
                for f in list_files(repo_path, "**/*.py"):
                    if module_hint in f and not self._is_test_file(f):
                        file_scores[f] = file_scores.get(f, 0) + 3.0

            if test_name:
                func_hint = test_name.replace("test_", "")
                symbols = symbol_search(repo_path, func_hint)
                for sym in symbols:
                    if not self._is_test_file(sym.file):
                        function_scores[sym.name] = function_scores.get(sym.name, 0) + 2.0
                        file_scores[sym.file] = file_scores.get(sym.file, 0) + 2.0

        max_file_score = max(file_scores.values(), default=1.0)
        candidate_files = [
            CandidateFile(file=f, confidence=min(1.0, score / max_file_score))
            for f, score in sorted(file_scores.items(), key=lambda x: -x[1])[:5]
        ]

        max_func_score = max(function_scores.values(), default=1.0)
        candidate_functions = [
            CandidateFunction(function=f, confidence=min(1.0, score / max_func_score))
            for f, score in sorted(function_scores.items(), key=lambda x: -x[1])[:5]
        ]

        reasoning = self._build_reasoning(bug, candidate_files, candidate_functions)

        return LocatorOutput(
            bug_id=bug.bug_id,
            candidate_files=candidate_files,
            candidate_functions=candidate_functions,
            reasoning=reasoning,
        )

    def _is_test_file(self, path: str) -> bool:
        """Check if a path is a test file."""
        return "/tests/" in path or path.startswith("tests/") or "/test_" in path

    def _extract_keywords(self, bug: Bug) -> list[str]:
        """Extract search keywords from the bug description."""
        keywords = []
        title_words = bug.title.lower().split()
        stop_words = {"a", "an", "the", "is", "are", "in", "on", "to", "for", "of", "and", "or", "not", "its"}
        keywords.extend(w for w in title_words if w not in stop_words and len(w) > 3)

        if bug.stack_trace:
            for line in bug.stack_trace.splitlines():
                if "File" in line and ".py" in line:
                    parts = line.split('"')
                    if len(parts) >= 2:
                        keywords.append(parts[1].split("/")[-1].replace(".py", ""))

        return keywords[:8]

    def _test_to_source_hint(self, test_path: str) -> str:
        """Convert a test file path to a source module hint."""
        name = Path(test_path).stem
        if name.startswith("test_"):
            return name[5:]
        return name

    def _build_reasoning(
        self,
        bug: Bug,
        files: list[CandidateFile],
        functions: list[CandidateFunction],
    ) -> str:
        parts = [f"Bug '{bug.title}' (type={bug.bug_type.value})."]
        if files:
            parts.append(f"Top file candidates: {', '.join(f.file for f in files[:3])}.")
        if functions:
            parts.append(f"Top function candidates: {', '.join(f.function for f in functions[:3])}.")
        return " ".join(parts)
