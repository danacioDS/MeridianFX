"""Meridian FX — Layer 2: Decision Engine.

Frozen against docs/Product_specification/Layer_02.md v3.4.1.
Consumes Layer 3 v5.0 §11.2 (PredictionArtifact) and Layer 4 v3.1.1 §7
(FeatureStore, DataQualityRegistry, FreshnessRegistry, DriftRegistry).

IMPLEMENTATION GOVERNANCE APPLIES — DO NOT INVENT CONTRACTS.
"""

from . import contracts, filter, gates, pipeline, quality, registries, sizing, validation
from .contracts import Decision, DecisionContext, SignalValidity
from .pipeline import DecisionPipeline, DecisionPipelineResult, PipelineInputs

__all__ = [
    "contracts",
    "filter",
    "gates",
    "quality",
    "sizing",
    "registries",
    "validation",
    "pipeline",
    "Decision",
    "DecisionContext",
    "SignalValidity",
    "DecisionPipeline",
    "DecisionPipelineResult",
    "PipelineInputs",
]