# PatchBench

A multi-agent software repair benchmark and bug-fixing system.

PatchBench evaluates how different LLM-agent architectures — **Single-Agent**,
**Chain-Based**, and **Multi-Agent** — perform on bug-fixing tasks over a suite
of synthetic repositories with injected bugs. Given a bug report, failing tests,
and repository context, an Orchestrator classifies the bug and routes it to
specialized Fixer agents; a Validator runs the tests and a Judge scores the
repair against a fixed set of metrics.

## Pipeline (target architecture)

```
Bug + Repo  ->  Orchestrator  ->  Locator  ->  Orchestrator (route)
            ->  Specialized Fixer  ->  Validator  --PASS-->  Judge  ->  Report
                                          |
                                          +--FAIL--> retry loop
```

## Project layout

```
patchbench/
  schemas/        Typed data contracts shared by every agent
    enums.py        BugType, Difficulty, Complexity, FixerType, CheckStatus, RunStatus
    bug.py          Bug                       (benchmark task / pipeline input)
    locator.py      LocatorOutput, CandidateFile, CandidateFunction
    fixer.py        FixerOutput
    validator.py    ValidatorOutput, TestResults
    judge.py        JudgeOutput
    trace.py        RunTrace                  (full end-to-end run record)
    baseline.py     SingleAgentOutput
  agents/         Orchestrator, Locator, Fixers, Validator, Judge
  tools/          RepoSearch, FileRead, TestRunner, Linter, StaticAnalysis
  baselines/      Single-Agent & Chain baselines
  metrics/        Fix Rate, Regression Rate, Overall Repair Score
  runner/         Benchmark driver + dataset loader
  cli.py          Command-line interface
benchmark/
  repos/          Clean reference repositories
  bugs/           The 20-bug v1 dataset (BUG_001 through BUG_020)
tests/            Unit tests (57 tests)
```

All schemas use **Pydantic v2** for runtime validation (confidence scores
constrained to `[0, 1]`, non-negative counts, closed enum vocabularies) and
clean JSON (de)serialization.

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

# Options: multi_agent, chain, single_agent, all
```

## Bug categories

The 20-bug dataset covers all 7 bug types:
- **logical_error** (10 bugs): wrong operators, incorrect conditions
- **state_bug** (5 bugs): overwrites, missing guards, mutation errors
- **api_mismatch** (1 bug): wrong argument passing style
- **dependency_config_bug** (1 bug): incorrect threshold constants
- **performance_bug** (1 bug): quadratic algorithms
- **syntax_error**: available via the pipeline (no dataset examples yet)
- **test_failure**: available via the pipeline (no dataset examples yet)

## Status

| Milestone | State |
|---|---|
| Repo skeleton + schema models | done |
| Dataset (20 bugs) | done |
| Tools (FileRead, Search, TestRunner, Lint) | done |
| Metrics (Fix Rate, Regression, Score) | done |
| Single-Agent baseline | done |
| Chain baseline | done |
| Multi-Agent system | done |
| CLI runner | done |
