"""PIT audit — behavior tests for KI-002-A.

These tests document the current behavior of DecisionEngineAdapter with
respect to the temporal contract (KI-002-D). They replace the previous
diagnostic tests that asserted `as_of == prediction_timestamp` — that
assertion was valid before KI-002-A step 2, but the adapter now derives
`as_of` from the data cutoff exposed by DecisionEngine.get_forecast().

What these tests verify:

- When `data_provider.last_date` is present, `as_of` equals it and is
  distinct from `prediction_timestamp`.
- When `data_provider.last_date` is missing, the adapter falls back to
  wall-clock and logs a warning. That fallback is temporary — see
  KNOWN_ISSUES.md KI-002-A step 3.

See KNOWN_ISSUES.md KI-002 for the full diagnosis.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from backend.src.meridian_fx.decision.contracts.prediction import MacroRegime

from backend.layer1.adapters.decision_engine_adapter import DecisionEngineAdapter

UTC = timezone.utc


def _make_adapter_with_forecast(forecast: dict) -> DecisionEngineAdapter:
    """Build a DecisionEngineAdapter whose underlying DecisionEngine
    returns the given forecast dict from get_forecast()."""
    engine = MagicMock()
    engine.get_forecast.return_value = forecast
    adapter = DecisionEngineAdapter(engine=engine)
    # Bypass the real MacroService to avoid network calls.
    adapter._get_macro_regime = lambda: MacroRegime(  # type: ignore[method-assign]
        risk="Risk-On", policy="Neutral", growth="High", inflation="Low"
    )
    return adapter


def _base_forecast(**overrides) -> dict:
    base = {
        "direction": "SHORT",
        "probability": 0.6,
        "expected_return": 0.002,
        "expected_volatility": 0.05,
        "actionable": False,
        "confidence": 0.6,
        "signal_strength": "moderate",
        "edge_ratio": 0.5,
        "net_return": 10.0,
        "position_size": 0.0,
        "model": {"version": "logistic-v1.0", "type": "logistic"},
        "shap": None,
        "data_provider": {
            "source": "yahoo",
            "fallback_used": False,
            "freshness": "FRESH",
            "last_price": 1.2345,
            "last_date": datetime(2026, 9, 14, 0, 0, tzinfo=UTC),
        },
    }
    base.update(overrides)
    return base


def test_as_of_uses_data_provider_last_date_when_present():
    """KI-002-A step 2: as_of comes from data_provider.last_date,
    not from the adapter's wall-clock."""
    last_date = datetime(2026, 9, 14, 0, 0, tzinfo=UTC)
    forecast = _base_forecast(
        data_provider={
            "source": "yahoo",
            "fallback_used": False,
            "freshness": "FRESH",
            "last_price": 1.2345,
            "last_date": last_date,
        }
    )
    adapter = _make_adapter_with_forecast(forecast)

    artifact = adapter.get_prediction_artifact("USD/CHF", horizon_days=5)

    assert artifact is not None
    assert artifact.as_of == last_date
    # prediction_timestamp is wall-clock, distinct from data cutoff
    assert artifact.prediction_timestamp != last_date
    assert artifact.prediction_timestamp > last_date


def test_as_of_falls_back_to_wall_clock_when_last_date_missing(caplog):
    """KI-002-A step 2 (temporary fallback): when data_provider.last_date
    is missing, the adapter falls back to wall-clock and logs a warning.

    This is a known temporary approximation; the fallback will be
    removed once the pipeline carries a full TemporalProvenance.
    """
    import logging

    forecast = _base_forecast(
        data_provider={
            "source": "none",
            "fallback_used": True,
            "freshness": "UNKNOWN",
            "last_price": 0.0,
            "last_date": None,
        }
    )
    adapter = _make_adapter_with_forecast(forecast)

    with caplog.at_level(logging.WARNING):
        artifact = adapter.get_prediction_artifact("USD/CHF", horizon_days=5)

    assert artifact is not None
    # Fallback: as_of == prediction_timestamp (both wall-clock)
    assert artifact.as_of == artifact.prediction_timestamp
    # Warning was logged
    assert any(
        "as_of fallback to wall-clock" in record.message
        for record in caplog.records
    )


def test_as_of_falls_back_when_data_provider_block_missing(caplog):
    """KI-002-A step 2: when data_provider is missing entirely, the
    adapter falls back to wall-clock."""
    import logging

    forecast = _base_forecast()
    del forecast["data_provider"]
    adapter = _make_adapter_with_forecast(forecast)

    with caplog.at_level(logging.WARNING):
        artifact = adapter.get_prediction_artifact("USD/CHF", horizon_days=5)

    assert artifact is not None
    assert artifact.as_of == artifact.prediction_timestamp
    assert any(
        "as_of fallback to wall-clock" in record.message
        for record in caplog.records
    )
