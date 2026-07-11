"""Benchmark driver — orchestrates full evaluation runs with trace persistence."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from patchbench.schemas import Bug, JudgeOutput, RunTrace
from patchbench.schemas.enums import RunStatus
from patchbench.agents.orchestrator import Orchestrator
from patchbench.baselines.single_agent import SingleAgentBaseline
from patchbench.baselines.chain import ChainBaseline
from patchbench.metrics.scoring import fix_rate, overall_repair_score, compute_all_metrics
from patchbench.runner.approval import ApprovalGate


@dataclass
class RunReport:
    """Summary report of a benchmark run."""

    architecture: str
    total_bugs: int
    bugs_fixed: int
    fix_rate: float
    avg_score: float
    total_runtime: float
    metrics: dict[str, float] = field(default_factory=dict)
    traces: list[RunTrace] = field(default_factory=list)


class BenchmarkRunner:
    """Drives the full benchmark evaluation with trace persistence.

    Supports three architectures:
    - "multi_agent": Full pipeline with Orchestrator routing + retries
    - "chain": Sequential Locator -> generic Fixer
    - "single_agent": One-shot repair

    Features:
    - Persists traces at each pipeline step (incremental)
    - Optional human approval gate
    - Computes all 10 metrics
    """

    def __init__(
        self,
        benchmark_dir: str | Path,
        timeout: int = 60,
        max_retries: int = 2,
        approval_gate: ApprovalGate | None = None,
        trace_dir: str | Path | None = None,
    ) -> None:
        self.benchmark_dir = Path(benchmark_dir)
        self.timeout = timeout
        self.max_retries = max_retries
        self.approval_gate = approval_gate or ApprovalGate(auto_approve=True)
        self.trace_dir = Path(trace_dir) if trace_dir else None

    def run_multi_agent(self, bugs: list[Bug]) -> RunReport:
        """Run the full multi-agent pipeline on all bugs."""
        orchestrator = Orchestrator(max_retries=self.max_retries, timeout=self.timeout)
        traces: list[RunTrace] = []
        total_start = time.time()

        for bug in bugs:
            repo_path = str(self.benchmark_dir.parent / bug.repo_path)
            trace = orchestrator.run(bug, repo_path)
            traces.append(trace)

            # Persist trace incrementally
            self._persist_trace(trace)

        total_runtime = time.time() - total_start
        judge_outputs = [t.judge_output for t in traces if t.judge_output]

        return RunReport(
            architecture="multi_agent",
            total_bugs=len(bugs),
            bugs_fixed=sum(1 for j in judge_outputs if j.fix_rate == 1.0),
            fix_rate=fix_rate(judge_outputs),
            avg_score=overall_repair_score(judge_outputs),
            total_runtime=round(total_runtime, 2),
            metrics=compute_all_metrics(judge_outputs),
            traces=traces,
        )

    def run_chain(self, bugs: list[Bug]) -> RunReport:
        """Run the chain baseline on all bugs."""
        chain = ChainBaseline(timeout=self.timeout)
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
            metrics=compute_all_metrics(judge_outputs),
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
            metrics=compute_all_metrics(judge_outputs),
        )

    def _persist_trace(self, trace: RunTrace) -> None:
        """Save a single trace to disk (incremental persistence)."""
        if not self.trace_dir:
            return
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        trace_path = self.trace_dir / f"{trace.run_id}.json"
        trace_path.write_text(json.dumps(trace.model_dump(), indent=2, default=str))

    def save_report(self, report: RunReport, output_path: str | Path) -> None:
        """Save a full run report to JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "architecture": report.architecture,
            "total_bugs": report.total_bugs,
            "bugs_fixed": report.bugs_fixed,
            "fix_rate": report.fix_rate,
            "avg_score": report.avg_score,
            "total_runtime": report.total_runtime,
            "metrics": report.metrics,
            "traces": [t.model_dump() for t in report.traces] if report.traces else [],
        }
        output_path.write_text(json.dumps(data, indent=2, default=str))
