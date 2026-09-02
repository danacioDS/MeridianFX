"""Layer 2 — SafeModeRegistry (risk-off control state).

Safe mode is a pipeline/control-plane decision consumed by Layer 1
(L1 v5.1 §7.7 StatusResponse.intelligence.safe_mode_state). Layer 1 consumes
SAFE_MODE; it does not activate it. Thresholds are versioned configuration.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator

from ..contracts.time import ensure_utc, utcnow


class SafeModeStateValue(StrEnum):
    ON = "ON"
    OFF = "OFF"
    UNKNOWN = "UNKNOWN"


class SafeModeConfig(BaseModel):
    """Versioned trigger thresholds (V0 = versioned configuration, L4 §2)."""

    model_config = ConfigDict(extra="forbid")

    vix_floor: float | None = None
    data_quality_floor: float | None = None
    policy_version: str = "1.0"


class SafeModeState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: SafeModeStateValue
    reason: str | None = None
    triggered_at: datetime | None = None

    @classmethod
    def off(cls) -> "SafeModeState":
        return cls(state=SafeModeStateValue.OFF, reason=None, triggered_at=None)


class SafeModeSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pair: str
    state: SafeModeStateValue
    reason: str | None
    as_of: datetime

    _tz = field_validator("as_of")(ensure_utc)


class SafeModeRegistry:
    """Tracks the SAFE_MODE state consumed by Layer 1 status reporting."""

    def __init__(self, config: SafeModeConfig | None = None) -> None:
        self._config = config or SafeModeConfig()
        self._state = SafeModeState.off()

    @property
    def config(self) -> SafeModeConfig:
        return self._config

    def get_state(self) -> SafeModeState:
        return self._state

    def activate(self, reason: str) -> SafeModeState:
        if self._state.state is not SafeModeStateValue.ON:
            self._state = SafeModeState(
                state=SafeModeStateValue.ON, reason=reason, triggered_at=utcnow()
            )
        return self._state

    def release(self) -> SafeModeState:
        self._state = SafeModeState.off()
        return self._state

    def evaluate(
        self,
        pair: str,
        as_of: datetime,
        vix: float | None,
        data_quality_score: float | None,
    ) -> SafeModeSnapshot:
        """Auto-activate from versioned thresholds; returns a snapshot."""
        reason: str | None = None
        if self._config.vix_floor is not None and vix is not None and vix >= self._config.vix_floor:
            reason = f"VIX at {vix} >= floor {self._config.vix_floor}"
        elif (
            self._config.data_quality_floor is not None
            and data_quality_score is not None
            and data_quality_score < self._config.data_quality_floor
        ):
            reason = f"data_quality {data_quality_score} < floor {self._config.data_quality_floor}"
        if reason is not None:
            self.activate(reason)
        state = self.get_state()
        return SafeModeSnapshot(
            pair=pair,
            state=state.state,
            reason=state.reason,
            as_of=ensure_utc(as_of),
        )