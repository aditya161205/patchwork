"""Command-line interface for running PatchBench evaluations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from patchbench.runner import load_all_bugs, BenchmarkRunner


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="patchbench",
        description="Run the PatchBench multi-agent repair benchmark.",
    )
    parser.add_argument(
        "--benchmark-dir",
        default="benchmark",
        help="Path to the benchmark directory (default: benchmark)",
    )
    parser.add_argument(
        "--architecture",
        choices=["multi_agent", "chain", "single_agent", "all"],
        default="all",
        help="Which architecture to evaluate (default: all)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON file for results (default: stdout)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Per-bug test timeout in seconds (default: 60)",
    )
    args = parser.parse_args()

    benchmark_dir = Path(args.benchmark_dir)
    if not benchmark_dir.is_dir():
        print(f"Error: benchmark directory not found: {benchmark_dir}", file=sys.stderr)
        sys.exit(1)

    bugs = load_all_bugs(benchmark_dir)
    print(f"Loaded {len(bugs)} bugs from {benchmark_dir}")

    runner = BenchmarkRunner(benchmark_dir, timeout=args.timeout)
    results = {}

    architectures = (
        ["multi_agent", "chain", "single_agent"]
        if args.architecture == "all"
        else [args.architecture]
    )

    for arch in architectures:
        print(f"\nRunning {arch} architecture...")
        if arch == "multi_agent":
            report = runner.run_multi_agent(bugs)
        elif arch == "chain":
            report = runner.run_chain(bugs)
        else:
            report = runner.run_single_agent(bugs)

        results[arch] = {
            "total_bugs": report.total_bugs,
            "bugs_fixed": report.bugs_fixed,
            "fix_rate": report.fix_rate,
            "avg_score": report.avg_score,
            "total_runtime": report.total_runtime,
        }
        print(f"  Fix rate: {report.fix_rate:.1%} ({report.bugs_fixed}/{report.total_bugs})")
        print(f"  Avg score: {report.avg_score:.2f}/10")
        print(f"  Runtime: {report.total_runtime:.2f}s")

    output = json.dumps(results, indent=2)
    if args.output:
        Path(args.output).write_text(output)
        print(f"\nResults saved to {args.output}")
    else:
        print(f"\n{'='*60}")
        print(output)


if __name__ == "__main__":
    main()
