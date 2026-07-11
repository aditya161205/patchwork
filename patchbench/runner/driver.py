"""Benchmark driver — orchestrates full evaluation runs."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from patchbench.schemas import Bug, JudgeOutput, RunTrace
from patchbench.schemas.enums import RunStatus
from patchbench.agents.orchestrator import Orchestrator
from patchbench.agents.locator import Locator
from patchbench.agents.fixer import get_fixer
from patchbench.agents.validator import Validator
from patchbench.agents.judge import Judge
from patchbench.baselines.single_agent import SingleAgentBaseline
from patchbench.baselines.chain import ChainBaseline
from patchbench.metrics.scoring import fix_rate, overall_repair_score


@dataclass
class RunReport:
    """Summary report of a benchmark run."""

    architecture: str
    total_bugs: int
    bugs_fixed: int
    fix_rate: float
    avg_score: float
    total_runtime: float
    traces: list[RunTrace] = field(default_factory=list)


class BenchmarkRunner:
    """Drives the full benchmark evaluation.

    Supports three architectures:
    - "multi_agent": Full pipeline with Orchestrator routing
    - "chain": Sequential Locator -> generic Fixer
    - "single_agent": One-shot repair
    """

    def __init__(self, benchmark_dir: str | Path, timeout: int = 60) -> None:
        self.benchmark_dir = Path(benchmark_dir)
        self.timeout = timeout

    def run_multi_agent(self, bugs: list[Bug]) -> RunReport:
        """Run the full multi-agent pipeline on all bugs."""
        orchestrator = Orchestrator()
        locator = Locator()
        validator = Validator(timeout=self.timeout)
        judge = Judge()

        traces: list[RunTrace] = []
        total_start = time.time()

        for bug in bugs:
            run_id = f"run_{uuid.uuid4().hex[:8]}"
            start = time.time()

            repo_path = str(self.benchmark_dir.parent / bug.repo_path)

            # Classify and route
            bug_type, complexity = orchestrator.classify(bug)
            fixer_type = orchestrator.select_fixer(bug_type)
            fixer = get_fixer(fixer_type)

            # Locate
            locator_output = locator.locate(bug, repo_path)

            # Fix
            fixer_output = fixer.fix(bug, locator_output, repo_path)

            # Validate
            validator_output = validator.validate(bug, fixer_output, repo_path)

            # Judge
            runtime = time.time() - start
            judge_output = judge.evaluate(
                bug, fixer_output, validator_output,
                runtime_seconds=round(runtime, 2),
                token_usage=0,
            )

            # Create trace
            final_status = judge_output.status
            trace = orchestrator.create_trace(
                run_id=run_id,
                bug=bug,
                fixer_type=fixer_type,
                complexity=complexity,
                locator_output=locator_output,
                fixer_output=fixer_output,
                validator_output=validator_output,
                judge_output=judge_output,
                tool_calls=4,
                subagents_spawned=3,
                final_status=final_status,
            )
            traces.append(trace)

        total_runtime = time.time() - total_start
        judge_outputs = [t.judge_output for t in traces if t.judge_output]

        return RunReport(
            architecture="multi_agent",
            total_bugs=len(bugs),
            bugs_fixed=sum(1 for j in judge_outputs if j.fix_rate == 1.0),
            fix_rate=fix_rate(judge_outputs),
            avg_score=overall_repair_score(judge_outputs),
            total_runtime=round(total_runtime, 2),
            traces=traces,
        )

    def run_chain(self, bugs: list[Bug]) -> RunReport:
        """Run the chain baseline on all bugs."""
        chain = ChainBaseline(timeout=self.timeout)
        judge = Judge()

        traces: list[RunTrace] = []
        judge_outputs: list[JudgeOutput] = []
        total_start = time.time()

        for bug in bugs:
            result = chain.run(bug, str(self.benchmark_dir.parent / bug.repo_path))
            j = JudgeOutput(
                bug_id=bug.bug_id,
                fix_rate=1.0 if result.status == RunStatus.SUCCESS else 0.0,
                runtime_seconds=result.runtime_seconds,
                token_usage=result.token_usage,
                files_modified=0,
                patch_size_lines=len(result.patch.splitlines()),
                regressions=0,
                judge_score=7.0 if result.status == RunStatus.SUCCESS else 2.0,
                status=result.status,
            )
            judge_outputs.append(j)

        total_runtime = time.time() - total_start

        return RunReport(
            architecture="chain",
            total_bugs=len(bugs),
            bugs_fixed=sum(1 for j in judge_outputs if j.fix_rate == 1.0),
            fix_rate=fix_rate(judge_outputs),
            avg_score=overall_repair_score(judge_outputs),
            total_runtime=round(total_runtime, 2),
        )

    def run_single_agent(self, bugs: list[Bug]) -> RunReport:
        """Run the single-agent baseline on all bugs."""
        baseline = SingleAgentBaseline(timeout=self.timeout)
        judge_outputs: list[JudgeOutput] = []
        total_start = time.time()

        for bug in bugs:
            result = baseline.run(bug, str(self.benchmark_dir.parent / bug.repo_path))
            j = JudgeOutput(
                bug_id=bug.bug_id,
                fix_rate=1.0 if result.status == RunStatus.SUCCESS else 0.0,
                runtime_seconds=result.runtime_seconds,
                token_usage=result.token_usage,
                files_modified=0,
                patch_size_lines=len(result.patch.splitlines()),
                regressions=0,
                judge_score=6.0 if result.status == RunStatus.SUCCESS else 1.5,
                status=result.status,
            )
            judge_outputs.append(j)

        total_runtime = time.time() - total_start

        return RunReport(
            architecture="single_agent",
            total_bugs=len(bugs),
            bugs_fixed=sum(1 for j in judge_outputs if j.fix_rate == 1.0),
            fix_rate=fix_rate(judge_outputs),
            avg_score=overall_repair_score(judge_outputs),
            total_runtime=round(total_runtime, 2),
        )

    def save_report(self, report: RunReport, output_path: str | Path) -> None:
        """Save a run report to JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "architecture": report.architecture,
            "total_bugs": report.total_bugs,
            "bugs_fixed": report.bugs_fixed,
            "fix_rate": report.fix_rate,
            "avg_score": report.avg_score,
            "total_runtime": report.total_runtime,
            "traces": [t.model_dump() for t in report.traces] if report.traces else [],
        }
        output_path.write_text(json.dumps(data, indent=2, default=str))
