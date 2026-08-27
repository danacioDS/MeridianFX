"""Layer 2 registries package (Prompt 10).

    * registries/decision.py    — DecisionRegistry (Patch P8, no delivery fields)
    * registries/opportunity.py — OpportunityRegistry + OpportunityScorer (§10)
    * registries/safe_mode.py   — SafeModeRegistry (consumed by Layer 1)
"""

from .decision import EXCLUDED_LAYER1_FIELDS, DecisionRegistry
from .opportunity import (
    DEFAULT_WEIGHTS,
    OpportunityRegistry,
    OpportunityScoreInput,
    OpportunityScoreResult,
    OpportunityScorer,
    RankedOpportunity,
)
from .safe_mode import (
    SafeModeConfig,
    SafeModeRegistry,
    SafeModeSnapshot,
    SafeModeState,
    SafeModeStateValue,
)

__all__ = [
    "DecisionRegistry",
    "EXCLUDED_LAYER1_FIELDS",
    "OpportunityRegistry",
    "OpportunityScorer",
    "OpportunityScoreInput",
    "OpportunityScoreResult",
    "RankedOpportunity",
    "DEFAULT_WEIGHTS",
    "SafeModeRegistry",
    "SafeModeConfig",
    "SafeModeSnapshot",
    "SafeModeState",
    "SafeModeStateValue",
]