"""Tests for the TemporalProvenance contract (KI-002-D design).

Covers T-D-1, T-D-2, T-D-3 from the design:

- T-D-1: PIT-7 enforced when all four timestamps are present.
- T-D-2: release_time=None accepted with reduced ordering.
- T-D-3: naive timestamps rejected (PIT-5).
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from meridian_fx.decision.contracts.temporal import (
    TemporalConfidence,
    TemporalProvenance,
)

UTC = timezone.utc


def _mk(**overrides) -> TemporalProvenance:
    defaults = dict(
        event_time=datetime(2026, 1, 5, 10, 0, tzinfo=UTC),
        release_time=datetime(2026, 1, 5, 10, 5, tzinfo=UTC),
        source_available_time=datetime(2026, 1, 5, 10, 10, tzinfo=UTC),
        system_available_time=datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
    )
    defaults.update(overrides)
    return TemporalProvenance(**defaults)


def test_t_d_1_pit7_enforced_when_all_four_present():
    """T-D-1: well-ordered chain is accepted."""
    p = _mk()
    assert p.event_time <= p.release_time <= p.source_available_time <= p.system_available_time


def test_t_d_1_pit7_violation_rejected():
    """T-D-1: out-of-order chain raises ValidationError."""
    with pytest.raises(ValidationError):
        _mk(
            event_time=datetime(2026, 1, 5, 12, 0, tzinfo=UTC),
            release_time=datetime(2026, 1, 5, 10, 5, tzinfo=UTC),
        )


def test_t_d_2_release_time_none_accepted():
    """T-D-2: release_time=None is accepted, reduced ordering enforced."""
    p = _mk(release_time=None)
    assert p.release_time is None
    assert p.event_time <= p.source_available_time <= p.system_available_time


def test_t_d_2_release_time_none_still_checks_reduced_ordering():
    """T-D-2: reduced ordering also enforced when release_time is None."""
    with pytest.raises(ValidationError):
        _mk(
            release_time=None,
            event_time=datetime(2026, 1, 5, 12, 0, tzinfo=UTC),
            source_available_time=datetime(2026, 1, 5, 10, 10, tzinfo=UTC),
        )


def test_t_d_3_naive_timestamps_rejected():
    """T-D-3: naive datetimes raise ValidationError (PIT-5)."""
    with pytest.raises(ValidationError):
        _mk(event_time=datetime(2026, 1, 5, 10, 0))


def test_t_d_3_non_utc_aware_converted_to_utc():
    """T-D-3: non-UTC aware timestamps are converted, not rejected."""
    from datetime import timedelta

    tz_plus_2 = timezone(timedelta(hours=2))
    p = _mk(
        event_time=datetime(2026, 1, 5, 12, 0, tzinfo=tz_plus_2),
    )
    assert p.event_time.tzinfo == UTC
    assert p.event_time.hour == 10


def test_default_confidence_levels():
    """release_time_confidence defaults to UNAVAILABLE. Others to VERIFIED."""
    p = _mk()
    assert p.event_time_confidence == TemporalConfidence.VERIFIED
    assert p.release_time_confidence == TemporalConfidence.UNAVAILABLE
    assert p.source_available_time_confidence == TemporalConfidence.VERIFIED
    assert p.system_available_time_confidence == TemporalConfidence.VERIFIED


def test_approximation_flag_settable():
    """Callers can mark individual timestamps as APPROXIMATED."""
    p = _mk(
        release_time_confidence=TemporalConfidence.APPROXIMATED,
        source_available_time_confidence=TemporalConfidence.APPROXIMATED,
    )
    assert p.release_time_confidence == TemporalConfidence.APPROXIMATED
    assert p.source_available_time_confidence == TemporalConfidence.APPROXIMATED
