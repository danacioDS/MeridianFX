"""Layer 2 domain contracts — package exports.

Governance: contracts are frozen against Layer 2 v3.4.1 (§3, 5, 7, 8, 9, 11, 12,
13), Layer 3 v5.0 (§11.2), and Layer 4 v3.1.1 (§7). DO NOT INVENT CONTRACTS.
"""

from .decision import (
    Decision,
    DecisionContext,
    RejectionReason,
    SignalValidity,
)
from .fusion import (
    ConfidenceCalculator,
    ConfidenceResult,
    DIRECTION_SIGN,
    Direction,
    FUSION_WEIGHTS,
    FusionEngine,
    FusionResult,
    NEUTRAL_THRESHOLD,
    RegimeWeights,
)
from .prediction import (
    REQUIRED_PREDICTION_FIELDS,
    ConfidenceInterval,
    MacroRegime,
    PredictionArtifact,
    Reproducibility,
    ShapValue,
)
from .providers import (
    DataQualityRegistry,
    DataQualitySnapshot,
    DataQualityStatus,
    DriftRegistry,
    DriftSnapshot,
    FeatureStore,
    FeatureValue,
    FreshnessRegistry,
    FreshnessSnapshot,
)
from .regime import (
    BASE_QUOTE_ALIGNMENT_TABLE,
    GLOBAL_ALIGNMENT_TABLE,
    GlobalRegime,
    PolicyRegime,
    REGIME_PROFILES,
    Regime,
    RegimeAlignmentInput,
    compute_regime_alignment,
    determine_regime,
)
from .signal import SignalComponents, SignalGenerator, SignalOutOfBoundsError
from .time import ensure_utc, utcnow

__all__ = [
    "Decision",
    "DecisionContext",
    "RejectionReason",
    "SignalValidity",
    "FusionEngine",
    "FusionResult",
    "RegimeWeights",
    "NEUTRAL_THRESHOLD",
    "FUSION_WEIGHTS",
    "Direction",
    "DIRECTION_SIGN",
    "ConfidenceCalculator",
    "ConfidenceResult",
    "SignalGenerator",
    "SignalComponents",
    "SignalOutOfBoundsError",
    "Regime",
    "GlobalRegime",
    "PolicyRegime",
    "compute_regime_alignment",
    "determine_regime",
    "GLOBAL_ALIGNMENT_TABLE",
    "BASE_QUOTE_ALIGNMENT_TABLE",
    "REGIME_PROFILES",
    "RegimeAlignmentInput",
    "PredictionArtifact",
    "ConfidenceInterval",
    "MacroRegime",
    "ShapValue",
    "Reproducibility",
    "REQUIRED_PREDICTION_FIELDS",
    "FeatureStore",
    "FeatureValue",
    "DataQualityRegistry",
    "DataQualitySnapshot",
    "DataQualityStatus",
    "FreshnessRegistry",
    "FreshnessSnapshot",
    "DriftRegistry",
    "DriftSnapshot",
    "ensure_utc",
    "utcnow",
]