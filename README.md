# PatchBench

A multi-agent software repair benchmark and bug-fixing system.

PatchBench evaluates how different LLM-agent architectures — **Single-Agent**,
**Chain-Based**, and **Multi-Agent** — perform on bug-fixing tasks over a suite
of synthetic repositories with injected bugs. Given a bug report, failing tests,
and repository context, an Orchestrator classifies the bug and routes it to
specialized Fixer agents; a Validator runs the tests and a Judge scores the
repair against a fixed set of metrics.

## Architecture

```
                          ┌─────────────┐
                          │  Bug + Repo  │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │ Orchestrator │  classify bug type + estimate complexity
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │   Locator    │  search for candidate files/functions
                          └──────┬───────┘
                                 │
                     ┌───────────▼───────────┐
                     │   Route to Fixer      │
                     │  (based on bug type)  │
                     └───────────┬───────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │          │           │           │           │
     ┌────▼───┐ ┌───▼───┐ ┌────▼───┐ ┌────▼───┐ ┌────▼───┐
     │ Syntax │ │ Logic │ │  API   │ │ State  │ │ Config │  ...
     │ Fixer  │ │ Fixer │ │ Fixer  │ │ Fixer  │ │ Fixer  │
     └────┬───┘ └───┬───┘ └────┬───┘ └────┬───┘ └────┬───┘
          └──────────┴──────────┼──────────┴──────────┘
                                │
                     ┌──────────▼──────────┐
                     │     Validator       │  sandbox → apply → test → lint
                     │  (cheat detection)  │  fail-to-pass / pass-to-pass
                     └──────────┬──────────┘
                        ┌───────┼───────┐
                     PASS│             │FAIL
                        │        retry loop
                  ┌─────▼─────┐  (up to 2x)
                  │   Judge   │
                  └─────┬─────┘
                        │
                  ┌─────▼─────┐
                  │  Report   │  trace + 10 metrics
                  └───────────┘
```

## Project layout

```
patchbench/
  schemas/        Typed data contracts (Pydantic v2)
  agents/         Orchestrator, Locator, 6 Fixers, Validator, Judge
    prompts.py    LLM prompt templates for each agent
  tools/          FileRead, RepoSearch, TestRunner, Linter, StaticAnalysis,
                  Sandbox, CheatDetector, Verifier
  baselines/      Single-Agent & Chain baselines
  metrics/        10 evaluation metrics
  runner/         Benchmark driver, dataset loader, IssueWatcher, ApprovalGate
  cli.py          Command-line interface
benchmark/
  repos/          Clean reference repository (ecommerce, 13 modules)
  bugs/           20-bug v1 dataset (BUG_001 – BUG_020)
results/          Benchmark run outputs + traces
tests/            73 unit tests
```

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Running the benchmark

```bash
# Run all architectures
patchbench --benchmark-dir benchmark

# Run a specific architecture
patchbench --architecture multi_agent --output results.json
```

## Verification backbone

The verifier pipeline provides:
- **Sandbox isolation**: repos are copied to temp directories before patch application — the original is never modified
- **Fail-to-pass analysis**: separately tracks whether the *target* failing tests now pass
- **Pass-to-pass analysis**: verifies previously-passing tests still pass (no regressions)
- **Cheat detection**: flags test-file edits, hardcoded returns, test deletion, noop assertions
- **Retry loop**: failed fixes are retried up to 2 times before scoring

## Issue watcher

For continuous operation, PatchBench includes a filesystem watcher:

```
issues/
  pending/      ← drop new bug directories here
  processing/   ← currently being fixed
  resolved/     ← successfully fixed
  failed/       ← could not be resolved
```

The watcher polls `pending/` and processes new issues through the pipeline with an optional human approval gate that shows the diff and waits for yes/no.

## 10 Evaluation metrics

| # | Metric | Description |
|---|--------|-------------|
| 1 | Fix Rate | Fraction of bugs fixed (binary per bug) |
| 2 | Fail-to-Pass Rate | Target failing tests that now pass |
| 3 | Pass-to-Pass Rate | Previously passing tests still passing |
| 4 | Regression Rate | Previously passing tests now failing |
| 5 | Localization Accuracy | Locator found the correct buggy file |
| 6 | Patch Minimality | Smaller patches score higher |
| 7 | Token Efficiency | Fix quality per token used |
| 8 | Runtime Efficiency | Fix quality per second |
| 9 | Cheat-Free Rate | Patches that pass cheat detection |
| 10 | Overall Repair Score | Composite 0–10 judge score |

## Benchmark results (heuristic agents, v1 dataset)

| Architecture | Fix Rate | Avg Score | Runtime |
|---|---|---|---|
| **Multi-Agent** | **5.0%** (1/20) | **4.22**/10 | 35.1s |
| Chain | 0.0% (0/20) | 2.00/10 | 17.6s |
| Single-Agent | 0.0% (0/20) | 1.50/10 | 4.8s |

The current agents use **heuristic pattern-matching** rather than LLMs. The multi-agent
pipeline outperforms baselines because specialized routing lets the correct fixer apply
targeted repair strategies. With LLM-backed agents (using the included prompt templates),
fix rates are expected to be significantly higher.

## Bug categories

The 20-bug dataset covers 5 of the 7 bug types:
- **logical_error** (10 bugs): wrong operators, incorrect conditions, bad comparisons
- **state_bug** (5 bugs): overwrites, missing guards, mutation errors
- **api_mismatch** (1 bug): wrong argument passing style
- **dependency_config_bug** (1 bug): incorrect threshold constants
- **performance_bug** (1 bug): quadratic algorithms

## Status

| Milestone | State |
|---|---|
| Repo skeleton + schema models | done |
| Dataset (20 bugs) | done |
| Tools (FileRead, Search, TestRunner, Sandbox, CheatDetector, Verifier) | done |
| Metrics (10 metrics) | done |
| Single-Agent baseline | done |
| Chain baseline | done |
| Multi-Agent system (with retry loop) | done |
| Verifier backbone (sandbox + cheat detection + fail-to-pass) | done |
| Issue watcher + human approval gate | done |
| LLM prompt templates | done |
| CLI runner | done |
| Benchmark results | done |
