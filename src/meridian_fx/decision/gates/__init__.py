"""Layer 2 hard gates package (Prompt 6).

    * gates/engine.py — HardGateEngine (precedence + thresholds)
    * gates/result.py — GateResult (Patch P3: direct signal_validity source)
"""

from .engine import (
    CORRELATION_THRESHOLD,
    DATA_QUALITY_THRESHOLD,
    ECONOMIC_FILTER_THRESHOLD,
    HardGateEngine,
    REGIME_ALIGNMENT_THRESHOLD,
)
from .result import GATE_PRECEDENCE, GateResult, GateState

__all__ = [
    "HardGateEngine",
    "GateResult",
    "GateState",
    "GATE_PRECEDENCE",
    "DATA_QUALITY_THRESHOLD",
    "ECONOMIC_FILTER_THRESHOLD",
    "CORRELATION_THRESHOLD",
    "REGIME_ALIGNMENT_THRESHOLD",
]