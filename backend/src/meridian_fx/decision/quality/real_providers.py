"""Real providers for the Decision Pipeline (v2.6).

Replaces StubFeatureStore with a real VIX provider backed by Yahoo Finance.
The other 3 registries (DataQuality, Freshness, Drift) remain Fake for now
(deferred to v2.7).
"""
from __future__ import annotations

import time
from typing import Optional

import yfinance as yf

from ..contracts.providers import FeatureValue
from ..contracts.temporal import TemporalConfidence, TemporalProvenance


class RealFeatureStore:
    """FeatureStore backed by real VIX data from Yahoo Finance.

    Caches the VIX value for 60 seconds to avoid repeated requests.
    Falls back to None if the fetch fails (the pipeline will mark the
    signal as UNAVAILABLE — no fallback logic is permitted).
    """
    version = "L4-feature-store-real-v1"

    def __init__(self, cache_ttl: int = 60) -> None:
        self._vix: Optional[float] = None
        self._vix_time: float = 0
        self._cache_ttl = cache_ttl

    def _fetch_vix(self) -> Optional[float]:
        """Fetch the current VIX from Yahoo Finance."""
        try:
            ticker = yf.Ticker("^VIX")
            hist = ticker.history(period="1d")
            if not hist.empty:
                return float(hist["Close"].iloc[-1])
        except Exception as e:
            print(f"⚠️  VIX fetch failed: {e}")
        return None

    def _get_cached_vix(self) -> Optional[float]:
        """Return cached VIX or fetch if cache is expired."""
        now = time.time()
        if self._vix is not None and (now - self._vix_time) < self._cache_ttl:
            return self._vix

        vix = self._fetch_vix()
        if vix is not None:
            self._vix = vix
            self._vix_time = now
        return vix

    def get_feature(self, feature_id, as_of) -> Optional[FeatureValue]:
        """Get feature by ID. Only 'vix' is implemented."""
        if feature_id == "vix":
            vix = self._get_cached_vix()
            if vix is None:
                return None
            # KI-002-A step 4: migrate to TemporalProvenance.
            # NOTE (KI-002-B): the VIX observation timestamp is not yet
            # captured from Yahoo (`hist.index[-1]`); it is approximated
            # as `as_of`. Both confidences are marked APPROXIMATED to
            # reflect this. See KNOWN_ISSUES.md KI-002-B.
            now = time.time()  # placeholder for system_available_time below
            import datetime as _dt

            return FeatureValue(
                feature_id="vix",
                value=vix,
                provenance=TemporalProvenance(
                    event_time=as_of,
                    release_time=None,
                    source_available_time=as_of,
                    system_available_time=_dt.datetime.now(_dt.timezone.utc),
                    event_time_confidence=TemporalConfidence.APPROXIMATED,
                    release_time_confidence=TemporalConfidence.UNAVAILABLE,
                    source_available_time_confidence=TemporalConfidence.APPROXIMATED,
                    system_available_time_confidence=TemporalConfidence.VERIFIED,
                ),
            )
        return None

    def set_vix(self, vix: Optional[float]) -> None:
        """Manual override for testing."""
        self._vix = vix
        self._vix_time = time.time() if vix is not None else 0
