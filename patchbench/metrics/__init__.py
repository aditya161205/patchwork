"""Evaluation metrics for PatchBench.

10 metrics covering fix quality, efficiency, and integrity:
1. fix_rate              — fraction of bugs fixed
2. fail_to_pass_rate    — target tests resolved
3. pass_to_pass_rate    — no regressions in passing tests
4. regression_rate      — previously passing tests now failing
5. localization_accuracy — locator found the right file
6. patch_minimality     — smaller patches score higher
7. token_efficiency     — quality per token
8. runtime_efficiency   — quality per second
9. cheat_free_rate      — passes cheat detection
10. overall_repair_score — composite 0-10 judge score
"""

from patchbench.metrics.scoring import (
    fix_rate,
    fail_to_pass_rate,
    pass_to_pass_rate,
    regression_rate,
    localization_accuracy,
    patch_minimality,
    token_efficiency,
    runtime_efficiency,
    cheat_free_rate,
    overall_repair_score,
    compute_judge_score,
    compute_all_metrics,
)

__all__ = [
    "fix_rate",
    "fail_to_pass_rate",
    "pass_to_pass_rate",
    "regression_rate",
    "localization_accuracy",
    "patch_minimality",
    "token_efficiency",
    "runtime_efficiency",
    "cheat_free_rate",
    "overall_repair_score",
    "compute_judge_score",
    "compute_all_metrics",
]
