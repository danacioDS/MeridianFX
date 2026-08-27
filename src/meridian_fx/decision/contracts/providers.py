"""Layer 4 v3.1.1 consumption interfaces — frozen cross-layer contract.

Layer 2 CONSUMES Layer 4 providers; it MUST NOT implement them (Prompt 5 P2,
Prompt 7 P5). These Protocol types describe the exact interface Layer 2
expects from the Layer 4 Data Layer:

  * FeatureStore.get_feature('vix', T)          — Patch P2 (VIX source of truth)
  * DataQualityRegistry                         — Patch P5 (source of truth)
  * FreshnessRegistry
  * DriftRegistry

Definitive interface: docs/Product_specification/Layer_04.md (v3.1.1 FROZEN).
Layer 4 is responsible for the concrete implementation.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .time import ensure_utc


class DataQualityStatus(StrEnum):
    """Layer 4 data quality categories (Patch P6: good ≥ 0.80, acceptable
    0.60–0.80, degraded < 0.60)."""

    GOOD = "good"
    ACCEPTABLE = "acceptable"
    DEGRADED = "degraded"


class FeatureValue(BaseModel):
    """A single feature observation returned by FeatureStore (L4 v3.1.1)."""

    model_config = ConfigDict(extra="forbid")

    feature_id: str
    value: float | None
    available_time: datetime

    _tz = field_validator("available_time")(ensure_utc)


class DataQualitySnapshot(BaseModel):
    """Layer 4 DataQualityRegistry snapshot.

    Only consumed as the Layer 2 SOURCE OF TRUTH (Patch P5/P6).
    """

    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0.0, le=1.0)
    status: DataQualityStatus | None = None
    as_of: datetime

    _tz = field_validator("as_of")(ensure_utc)


class FreshnessSnapshot(BaseModel):
    """Layer 4 FreshnessRegistry snapshot."""

    model_config = ConfigDict(extra="forbid")

    age_hours: float = Field(ge=0.0)
    as_of: datetime

    _tz = field_validator("as_of")(ensure_utc)

    @property
    def freshness(self) -> float:
        """freshness = exp(-age_hours / τ_fresh), τ_fresh = 24 (L2 §9)."""
        return max(0.0, min(1.0, pow(2.718281828459045, -self.age_hours / 24.0)))


class DriftSnapshot(BaseModel):
    """Layer 4 DriftRegistry snapshot."""

    model_config = ConfigDict(extra="forbid")

    psi: float | None = None
    as_of: datetime

    _tz = field_validator("as_of")(ensure_utc)


@runtime_checkable
class FeatureStore(Protocol):
    """Layer 4 FeatureStore — the ONLY source of features for Layer 2."""

    def get_feature(self, feature_id: str, as_of: datetime) -> FeatureValue | None: ...

    @property
    def version(self) -> str: ...


@runtime_checkable
class DataQualityRegistry(Protocol):
    """Layer 4 Data Quality Registry — SOURCE OF TRUTH (Patch P5).

    Layer 2 MUST NOT implement a duplicate registry.
    """

    def get_data_quality(self, as_of: datetime) -> DataQualitySnapshot | None: ...

    @property
    def version(self) -> str: ...


@runtime_checkable
class FreshnessRegistry(Protocol):
    """Layer 4 Freshness Registry (Patch P5)."""

    def get_freshness(self, as_of: datetime) -> FreshnessSnapshot | None: ...

    @property
    def version(self) -> str: ...


@runtime_checkable
class DriftRegistry(Protocol):
    """Layer 4 Drift Registry (Patch P5)."""

    def get_drift(self, as_of: datetime) -> DriftSnapshot | None: ...

    @property
    def version(self) -> str: ...