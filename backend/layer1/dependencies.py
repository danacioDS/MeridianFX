"""
Shared singletons for Layer 1 routers.

Importing this module from multiple routers ensures a single
PipelineBridge instance across the whole app:
  - one DecisionEngine
  - one set of 9 Logistic_24 models in memory
  - one decision cache

Without this module, canonical.py and ranking.py would each create
their own PipelineBridge, doubling memory usage (9 models × 2) and
fragmenting the cache.
"""
from backend.layer2.pipeline_bridge import PipelineBridge
from backend.src.meridian_fx.decision.pipeline import DecisionPipeline
from backend.src.meridian_fx.decision.validation.validate_integration import (
    StubDataQualityRegistry,
    StubFreshnessRegistry,
    StubDriftRegistry,
)
from backend.src.meridian_fx.decision.quality.real_providers import RealFeatureStore


pipeline = DecisionPipeline(
    feature_store=RealFeatureStore(),
    data_quality_registry=StubDataQualityRegistry(0.90),
    freshness_registry=StubFreshnessRegistry(3.0),
    drift_registry=StubDriftRegistry(0.05),
)

bridge = PipelineBridge(pipeline)
