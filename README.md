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
  schemas/        Typed data contracts shared by every agent  <- implemented
    enums.py        BugType, Difficulty, Complexity, FixerType, CheckStatus, RunStatus
    bug.py          Bug                       (benchmark task / pipeline input)
    locator.py      LocatorOutput, CandidateFile, CandidateFunction
    fixer.py        FixerOutput
    validator.py    ValidatorOutput, TestResults
    judge.py        JudgeOutput
    trace.py        RunTrace                  (full end-to-end run record)
    baseline.py     SingleAgentOutput
  agents/         Orchestrator, Locator, Fixers, Validator, Judge   (skeleton)
  tools/          RepoSearch, FileRead, TestRunner, ...              (skeleton)
  baselines/      Single-Agent & Chain baselines                    (skeleton)
  metrics/        Fix Rate, Regression Rate, Overall Repair Score    (skeleton)
  runner/         Benchmark driver                                  (skeleton)
benchmark/        The 20-bug v1 dataset                             (skeleton)
tests/            Unit tests
```

Schemas are built first because every later milestone communicates through
them. All schemas use **Pydantic v2** for runtime validation (confidence scores
constrained to `[0, 1]`, non-negative counts, closed enum vocabularies) and
clean JSON (de)serialization.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Status

| Milestone | State |
|---|---|
| Repo skeleton + schema models | done |
| Dataset (20 bugs) | planned |
| Single-Agent baseline | planned |
| Chain baseline | planned |
| Multi-Agent system | planned |
