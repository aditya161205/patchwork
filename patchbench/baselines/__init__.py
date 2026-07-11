"""Baseline systems for comparison against the multi-agent pipeline.

- SingleAgentBaseline: One-shot repair with no localization or routing
- ChainBaseline: Sequential pipeline without specialized routing
"""

from patchbench.baselines.single_agent import SingleAgentBaseline
from patchbench.baselines.chain import ChainBaseline

__all__ = ["SingleAgentBaseline", "ChainBaseline"]
