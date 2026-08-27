"""Layer 2 decision-quality package (Prompt 7).

    * quality/models.py — DecisionQuality model (Patch P6 status mapping)
    * quality/engine.py  — DecisionQualityEngine (consumes L4 registries, P5)
"""

from .engine import (
    HIGH_QUALITY_THRESHOLD,
    DecisionQualityEngine,
    MODERATE_QUALITY_THRESHOLD,
    PSI_THRESHOLD,
    TAU_FRESHNESS_HOURS,
)
from .models import (
    DecisionQuality,
    DecisionQualityComponents,
    FallbackStatus,
    QualityLevel,
)

__all__ = [
    "DecisionQualityEngine",
    "DecisionQuality",
    "DecisionQualityComponents",
    "FallbackStatus",
    "QualityLevel",
    "HIGH_QUALITY_THRESHOLD",
    "MODERATE_QUALITY_THRESHOLD",
    "PSI_THRESHOLD",
    "TAU_FRESHNESS_HOURS",
]