"""Layer 2 v3.4.1 §8/§12 — Hard gate result and signal validity.

Gate precedence (unchanged):
    1. UNAVAILABLE  2. INVALID  3. CONCENTRATION  4. DATA_QUALITY
    5. ECONOMIC_FILTER  6. CORRELATION  7. REGIME_MISALIGNMENT

Patch P3: GateResult.signal_validity is assigned DIRECTLY to
Decision.signal_validity (no transformation or mapping).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from ..contracts.decision import RejectionReason, SignalValidity


class GateState(StrEnum):
    """The seven hard gates, declared in precedence order (§8)."""

    UNAVAILABLE = "unavailable"
    INVALID = "invalid"
    CONCENTRATION = "concentration"
    DATA_QUALITY = "data_quality"
    ECONOMIC_FILTER = "economic_filter"
    CORRELATION = "correlation"
    REGIME_MISALIGNMENT = "regime_misalignment"


GATE_PRECEDENCE: tuple[GateState, ...] = (
    GateState.UNAVAILABLE,
    GateState.INVALID,
    GateState.CONCENTRATION,
    GateState.DATA_QUALITY,
    GateState.ECONOMIC_FILTER,
    GateState.CORRELATION,
    GateState.REGIME_MISALIGNMENT,
)


class GateResult(BaseModel):
    """Result of the HardGateEngine evaluation (no structural changes)."""

    model_config = ConfigDict(extra="forbid")

    gate_results: dict[GateState, bool]  # gate → passed?
    all_passed: bool
    first_failing_gate: GateState | None
    thresholds_used: dict[str, float]
    signal_validity: SignalValidity  # Patch P3 — direct source for Decision
    rejection_reason: RejectionReason | None = None
    degraded_warnings: list[str] = []

    def failing_gates(self) -> list[GateState]:
        return [g for g in GATE_PRECEDENCE if not self.gate_results.get(g, False)]