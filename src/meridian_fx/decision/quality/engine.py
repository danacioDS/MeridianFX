"""Layer 2 v3.4.1 §9 — Decision quality engine.

Patch P5: Layer 2 CONSUMES the Layer 4 DataQualityRegistry / FreshnessRegistry
/ DriftRegistry as the source of truth for data-quality metrics. It MUST NOT
implement a duplicate registry.
Patch P6: data_quality_status → components.data_quality via
    good >= 0.80, acceptable 0.60-0.80, degraded < 0.60.
"""

from __future__ import annotations

import math

from ..contracts.providers import (
    DataQualityRegistry,
    DataQualitySnapshot,
    DriftRegistry,
    FreshnessRegistry,
)
from .models import (
    DecisionQuality,
    DecisionQualityComponents,
    FallbackStatus,
    QualityLevel,
)

TAU_FRESHNESS_HOURS = 24.0
PSI_THRESHOLD = 0.20
WEIGHT_CONFIDENCE = 0.30
WEIGHT_FRESHNESS = 0.25
WEIGHT_REGIME_ALIGNMENT = 0.20
WEIGHT_DATA_QUALITY = 0.15
WEIGHT_DRIFT = 0.10

HIGH_QUALITY_THRESHOLD = 0.70
MODERATE_QUALITY_THRESHOLD = 0.50


class DecisionQualityEngine:
    """Computes context-oriented decision quality (§9)."""

    @staticmethod
    def freshness_from_age(age_hours: float) -> float:
        """freshness = exp(-age_hours / 24)."""
        return max(0.0, min(1.0, math.exp(-age_hours / TAU_FRESHNESS_HOURS)))

    @staticmethod
    def drift_score_from_psi(psi: float | None) -> tuple[float, str]:
        """drift_score = 1 - min(1, PSI/0.20); PSI missing → 0.50 FALLBACK."""
        if psi is None:
            return 0.50, "FALLBACK"
        return max(0.0, min(1.0, 1.0 - min(1.0, psi / PSI_THRESHOLD))), "VALID"

    @staticmethod
    def _level(score: float) -> QualityLevel:
        if score >= HIGH_QUALITY_THRESHOLD:
            return QualityLevel.HIGH
        if score >= MODERATE_QUALITY_THRESHOLD:
            return QualityLevel.MODERATE
        return QualityLevel.LOW

    def compute_from_providers(
        self,
        as_of,
        confidence: float,
        regime_alignment: float,
        data_quality_registry: DataQualityRegistry,
        freshness_registry: FreshnessRegistry,
        drift_registry: DriftRegistry,
        age_hours_override: float | None = None,
        psi_override: float | None = None,
        dq_override: DataQualitySnapshot | None = None,
    ) -> DecisionQuality:
        """Consume Layer 4 registries as SOURCE OF TRUTH (Patch P5)."""
        dq = dq_override or data_quality_registry.get_data_quality(as_of)
        if dq is None:
            raise ValueError("DATA_QUALITY_REGISTRY_MISSING — required intelligence unavailable")

        if age_hours_override is not None:
            age_hours = age_hours_override
        else:
            freshness_snapshot = freshness_registry.get_freshness(as_of)
            if freshness_snapshot is None:
                raise ValueError("FRESHNESS_REGISTRY_MISSING — required intelligence unavailable")
            age_hours = freshness_snapshot.age_hours

        if psi_override is not None:
            psi: float | None = psi_override
        else:
            drift_snapshot = drift_registry.get_drift(as_of)
            psi = None if drift_snapshot is None else drift_snapshot.psi

        drift_score, drift_status = self.drift_score_from_psi(psi)
        status = dq.status or self._status_from_score(dq.score)
        return self._compute(
            confidence=confidence,
            age_hours=age_hours,
            regime_alignment=regime_alignment,
            data_quality_score=dq.score,
            data_quality_status=status,
            drift_score=drift_score,
            drift_status=drift_status,
        )

    def compute_direct(
        self,
        confidence: float,
        age_hours: float,
        regime_alignment: float,
        data_quality_score: float,
        data_quality_status: str | None = None,
        drift_psi: float | None = None,
    ) -> DecisionQuality:
        """Numeric path (used by direct unit tests)."""
        drift_score, drift_status = self.drift_score_from_psi(drift_psi)
        return self._compute(
            confidence=confidence,
            age_hours=age_hours,
            regime_alignment=regime_alignment,
            data_quality_score=data_quality_score,
            data_quality_status=data_quality_status
            or self._status_from_score(data_quality_score),
            drift_score=drift_score,
            drift_status=drift_status,
        )

    def _compute(
        self,
        confidence: float,
        age_hours: float,
        regime_alignment: float,
        data_quality_score: float,
        data_quality_status: str,
        drift_score: float,
        drift_status: str,
    ) -> DecisionQuality:
        freshness = self.freshness_from_age(age_hours)
        confidence = max(0.0, min(1.0, confidence))
        regime_alignment = max(0.0, min(1.0, regime_alignment))
        data_quality_score = max(0.0, min(1.0, data_quality_score))

        score = (
            WEIGHT_CONFIDENCE * confidence
            + WEIGHT_FRESHNESS * freshness
            + WEIGHT_REGIME_ALIGNMENT * regime_alignment
            + WEIGHT_DATA_QUALITY * data_quality_score
            + WEIGHT_DRIFT * drift_score
        )
        score = max(0.0, min(1.0, score))

        normalization_status = "FALLBACK" if confidence is None else "VALID"

        return DecisionQuality(
            score=round(score, 6),
            components=DecisionQualityComponents(
                confidence=round(confidence, 6),
                freshness=round(freshness, 6),
                regime_alignment=round(regime_alignment, 6),
                data_quality=data_quality_status,
                data_quality_score=round(data_quality_score, 6),
                drift_score=round(drift_score, 6),
            ),
            level=self._level(score),
            fallback_status=FallbackStatus(
                drift=drift_status,
                normalization=normalization_status,
            ),
        )

    @staticmethod
    def _status_from_score(score: float) -> str:
        """Patch P6 mapping: good >= 0.80, acceptable 0.60-0.80, degraded < 0.60."""
        return "good" if score >= 0.80 else "acceptable" if score >= 0.60 else "degraded"