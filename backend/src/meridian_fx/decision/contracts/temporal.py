"""Temporal provenance contracts — Layer 4 PIT-7 temporal chain.

Defines the full temporal provenance of a data observation, with
per-timestamp confidence levels. This replaces the previous approach
where a single `available_time: datetime` field collapsed multiple
distinct temporal concepts (event_time, release_time,
source_available_time, system_available_time) into one value.

See KNOWN_ISSUES.md KI-002-D for the design decision that led to this
type.
"""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from .time import ensure_utc


class TemporalConfidence(StrEnum):
    """Confidence level of an individual temporal value.

    - VERIFIED: the timestamp was captured directly from a source that
      exposes it (e.g. market candle timestamp from Yahoo).
    - APPROXIMATED: the timestamp was inferred from another timestamp
      because the source does not expose it (e.g. FRED release_time
      approximated from observation_date, or market release_time
      approximated from the candle timestamp).
    - UNAVAILABLE: the timestamp could not be determined.
    """

    VERIFIED = "verified"
    APPROXIMATED = "approximated"
    UNAVAILABLE = "unavailable"


class TemporalProvenance(BaseModel):
    """Temporal chain for a data observation (Layer 4 §3, PIT-7).

    Invariant (PIT-7, enforced when all four values are present):

        event_time <= release_time <= source_available_time
                   <= system_available_time

    Every timestamp carries its own confidence level. This makes the
    approximation explicit at the field level, avoiding the trap of
    declaring a value "verified" simply because a numeric timestamp is
    present.
    """

    model_config = ConfigDict(extra="forbid")

    event_time: datetime
    release_time: datetime | None = None
    source_available_time: datetime
    system_available_time: datetime

    event_time_confidence: TemporalConfidence = TemporalConfidence.VERIFIED
    release_time_confidence: TemporalConfidence = TemporalConfidence.UNAVAILABLE
    source_available_time_confidence: TemporalConfidence = TemporalConfidence.VERIFIED
    system_available_time_confidence: TemporalConfidence = TemporalConfidence.VERIFIED

    _tz = field_validator(
        "event_time",
        "release_time",
        "source_available_time",
        "system_available_time",
    )(ensure_utc)

    @model_validator(mode="after")
    def _check_ordering(self) -> "TemporalProvenance":
        """Enforce PIT-7 when release_time is present, and the reduced
        ordering (event_time <= source_available_time <= system_available_time)
        otherwise."""
        if self.release_time is not None:
            if not (
                self.event_time
                <= self.release_time
                <= self.source_available_time
                <= self.system_available_time
            ):
                raise ValueError(
                    "PIT-7 violation: expected "
                    "event_time <= release_time <= source_available_time "
                    "<= system_available_time"
                )
        else:
            if not (
                self.event_time
                <= self.source_available_time
                <= self.system_available_time
            ):
                raise ValueError(
                    "Temporal ordering violation: expected "
                    "event_time <= source_available_time <= system_available_time"
                )
        return self


__all__ = ["TemporalConfidence", "TemporalProvenance"]
