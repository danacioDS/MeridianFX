"""Layer 2 — Decision pipeline orchestrator.

Composes signals → fusion → costs → economic filter → decision quality
→ hard gates → position sizing → Decision (L2 §2 architecture).

Patch compliance:
  P1 Decision.prediction_id references a complete PredictionArtifact.
  P2 VIX ONLY via FeatureStore.get_feature('vix', T).
  P3 GateResult.signal_validity assigned DIRECTLY to Decision.signal_validity.
  P5 L4 DataQualityRegistry/FreshnessRegistry/DriftRegistry consumed.
  P7 Capacity check is secondary; GateResult never modified by sizing.
  P8 No Layer 1 delivery fields stored.

This module is orchestration glue — it defines NO new contracts.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from pydantic import ValidationError

from .contracts import (
    ConfidenceCalculator,
    DataQualityRegistry,
    Decision,
    DecisionContext,
    Direction,
    DriftRegistry,
    FeatureStore,
    FreshnessRegistry,
    FusionEngine,
    PredictionArtifact,
    RejectionReason,
    SignalComponents,
    SignalGenerator,
    SignalOutOfBoundsError,
    SignalValidity,
    compute_regime_alignment,
    determine_regime,
    utcnow,
)
from .contracts.signal import raw_macro_score, raw_quant_score, raw_rag_score
from .filter import CostCalculator, EconomicFilter, EdgeThresholdInvalidError, VixUnavailableError
from .gates import GateResult, HardGateEngine
from .quality import DecisionQualityEngine
from .sizing import PositionSizingEngine


@dataclass
class PipelineInputs:
    """Everything Layer 2 needs beyond the frozen PredictionArtifact.

    Macro differentials, RAG scores, policy rates, alignment, exposure and PIT
    availability come from Layer 4 data; required_minimum_edge / base_size /
    exposure caps are versioned policy configuration (L4 §2).
    """

    artifact: PredictionArtifact
    policy_differential: float = 0.0
    growth_differential: float = 0.0
    normalized_rate_differential: float = 0.0
    base_signal: float = 0.0
    quote_signal: float = 0.0
    base_rate: float = 0.0
    quote_rate: float = 0.0
    global_regime: str = "Neutral"
    base_policy: str = "Neutral"
    quote_policy: str = "Neutral"
    required_minimum_edge: float = 10.0  # bps policy
    base_size: float = 100_000.0
    current_exposure: float = 0.0
    max_exposure: float = 1_000_000.0
    historical_reliability: float = 0.0  # rolling 3-month DA [0, 1]
    model_confidence_p5_width: float = 0.0
    model_confidence_p95_width: float = 1.0
    max_abs_correlation: float | None = None
    data_coverage_pct: float | None = None
    age_hours: float | None = None  # freshness override (else L4 FreshnessRegistry)
    model_loaded: bool = True
    required_data_missing: bool = False

    # PIT availability (Layer 4 Synthetic Datasets D / D2 acceptance)::
    #   D  → derived.available_time < max(inputs)  → Gate #2 INVALID
    #   D2 → derived.available_time == max(inputs) → Gate #2 VALID
    derived_available_time: datetime | None = None
    input_available_times: list[datetime] = field(default_factory=list)


@dataclass
class DecisionPipelineResult:
    decision: Decision
    signals: SignalComponents | None = None
    regime: str | None = None
    fusion: dict | None = None
    costs: dict | None = None
    economic: dict | None = None
    quality: dict | None = None
    gate: GateResult | None = None
    sizing: dict | None = None
    vix: float | None = None


class DecisionPipeline:
    """End-to-end Layer 2 pipeline (PREDICTION → … → AUDIT)."""

    def __init__(
        self,
        feature_store: FeatureStore,
        data_quality_registry: DataQualityRegistry,
        freshness_registry: FreshnessRegistry,
        drift_registry: DriftRegistry,
    ) -> None:
        self.feature_store = feature_store
        self.data_quality_registry = data_quality_registry
        self.freshness_registry = freshness_registry
        self.drift_registry = drift_registry

        self._signal_generator = SignalGenerator()
        self._confidence = ConfidenceCalculator()
        self._costs = CostCalculator()
        self._economic = EconomicFilter()
        self._quality = DecisionQualityEngine()
        self._gates = HardGateEngine()
        self._sizing = PositionSizingEngine()

    # ------------------------------------------------------------------
    def build(self, inputs: PipelineInputs) -> DecisionPipelineResult:
        artifact = inputs.artifact
        as_of = artifact.as_of

        # ---- Signals (§3) --------------------------------------------------
        quant = raw_quant_score(artifact.probability_up)
        macro = raw_macro_score(
            inputs.policy_differential,
            inputs.growth_differential,
            inputs.normalized_rate_differential,
        )
        rag = raw_rag_score(inputs.base_signal, inputs.quote_signal)
        try:
            signals = SignalComponents(
                quant_score=quant, macro_score=macro, rag_score=rag
            )
        except (SignalOutOfBoundsError, ValidationError):
            # pydantic wraps validator ValueError into ValidationError.
            return self._out_of_bounds_decision(inputs, quant, macro, rag)

        # ---- Regime + Fusion (§4/§5) --------------------------------------
        regime = determine_regime(artifact.macro_regime.model_dump())

        return self._build_valid_path(inputs, artifact, as_of, signals, regime)

    # ------------------------------------------------------------------
    def _build_valid_path(
        self,
        inputs: PipelineInputs,
        artifact: PredictionArtifact,
        as_of: datetime,
        signals: SignalComponents,
        regime: str,
    ) -> DecisionPipelineResult:
        fusion = FusionEngine().fuse(signals, regime)
        model_confidence = self._confidence.model_confidence_from_interval(
            width=artifact.confidence_interval.width,
            p5_width=inputs.model_confidence_p5_width,
            p95_width=inputs.model_confidence_p95_width,
        )
        confidence_result = self._confidence.compute(
            fusion_score=fusion.fusion_score,
            quant_score=signals.quant_score.value,
            macro_score=signals.macro_score.value,
            rag_score=signals.rag_score.value,
            model_confidence=model_confidence,
            historical_reliability=inputs.historical_reliability,
        )

        # ---- VIX from L4 ONLY (P2) ---------------------------------------
        vix: float | None = None
        try:
            vix = self._costs.vix_from_feature_store(artifact.pair, self.feature_store, as_of)
        except VixUnavailableError:
            vix = None  # Gate #1 → UNAVAILABLE; NO alternative VIX path.

        costs = None
        economic = None
        if vix is not None:
            costs = self._costs.calculate_total_cost(artifact.pair, vix)
            try:
                economic = self._economic.apply(
                    expected_return=artifact.expected_return,
                    direction=fusion.direction,
                    base_rate=inputs.base_rate,
                    quote_rate=inputs.quote_rate,
                    horizon_days=artifact.horizon_days,
                    total_cost=costs.total_cost,
                    required_minimum_edge=inputs.required_minimum_edge,
                )
            except EdgeThresholdInvalidError:
                return self._invalid_edge_decision(inputs, artifact, signals, regime)

        # ---- Decision quality (§9, P5: consume L4 registries) -------------
        regime_alignment = compute_regime_alignment(
            inputs.global_regime,
            inputs.base_policy,
            inputs.quote_policy,
            fusion.direction.value,
        )
        quality = None
        quality_error: Exception | None = None
        try:
            quality = self._quality.compute_from_providers(
                as_of=as_of,
                confidence=confidence_result.confidence,
                regime_alignment=regime_alignment,
                data_quality_registry=self.data_quality_registry,
                freshness_registry=self.freshness_registry,
                drift_registry=self.drift_registry,
                age_hours_override=inputs.age_hours,
            )
        except Exception as exc:  # pragma: no cover - defensive
            quality_error = exc

        # ---- Hard gates (§8/§12) ------------------------------------------
        context = DecisionContext(
            pair=artifact.pair,
            prediction_timestamp=artifact.prediction_timestamp,
            as_of=as_of,
            horizon_days=artifact.horizon_days,
            model_loaded=inputs.model_loaded,
            required_data_missing=inputs.required_data_missing or quality_error is not None,
            vix=vix,
            quant_score=signals.quant_score.value,
            macro_score=signals.macro_score.value,
            rag_score=signals.rag_score.value,
            required_minimum_edge=inputs.required_minimum_edge,
            derived_available_time=inputs.derived_available_time,
            input_available_times=inputs.input_available_times,
            current_exposure=inputs.current_exposure,
            max_exposure=inputs.max_exposure,
            data_quality_score=quality.components.data_quality_score if quality else None,
            data_quality_status=quality.components.data_quality if quality else None,
            expected_return=artifact.expected_return,
            base_rate=inputs.base_rate,
            quote_rate=inputs.quote_rate,
            direction=fusion.direction,
            total_cost=costs.total_cost if costs else None,
            edge_ratio=economic.edge_ratio if economic else None,
            net_return=economic.net_return if economic else None,
            max_abs_correlation=inputs.max_abs_correlation,
            regime_alignment=regime_alignment,
            age_hours=inputs.age_hours,
            data_coverage_pct=inputs.data_coverage_pct,
        )
        gate = self._gates.evaluate(context)

        # ---- Position sizing (§11, P7 secondary capacity check) ------------
        sizing = self._sizing.calculate(
            actionable=economic.actionable if economic else False,
            all_gates_passed=gate.all_passed,
            rejection_reason=gate.rejection_reason,
            base_size=inputs.base_size,
            edge_ratio=economic.edge_ratio if economic else 0.0,
            decision_quality=quality.score if quality else 0.0,
            vix=vix,
            current_exposure=inputs.current_exposure,
            max_exposure=inputs.max_exposure,
        )

        # ---- Decision assembly ---------------------------------------------
        actionable = (economic.actionable if economic else False) and gate.all_passed
        rejection_reason = gate.rejection_reason or sizing.rejection_reason
        decision = Decision(
            decision_id=str(uuid.uuid4()),
            prediction_id=artifact.prediction_id,  # P1 — complete artifact ref
            pair=artifact.pair,
            timestamp=utcnow(),
            as_of=as_of,
            horizon_days=artifact.horizon_days,
            actionable=actionable,
            direction=fusion.direction,
            confidence=confidence_result.confidence,
            edge_ratio=economic.edge_ratio if economic else 0.0,
            net_return=economic.net_return if economic else 0.0,
            position_size=sizing.position_size,
            rejection_reason=rejection_reason,
            signal_validity=gate.signal_validity,  # P3 — DIRECT assignment
        )

        return DecisionPipelineResult(
            decision=decision,
            signals=signals,
            regime=regime,
            fusion=fusion.model_dump(),
            costs=costs.model_dump() if costs else None,
            economic=economic.model_dump() if economic else None,
            quality=quality.model_dump() if quality else None,
            gate=gate,
            sizing=sizing.model_dump(),
            vix=vix,
        )

    # ------------------------------------------------------------------
    def _out_of_bounds_decision(
        self, inputs: PipelineInputs, quant: float, macro: float, rag: float
    ) -> DecisionPipelineResult:
        artifact = inputs.artifact
        decision = Decision(
            decision_id=str(uuid.uuid4()),
            prediction_id=artifact.prediction_id,
            pair=artifact.pair,
            timestamp=utcnow(),
            as_of=artifact.as_of,
            horizon_days=artifact.horizon_days,
            actionable=False,
            direction=Direction.NEUTRAL,
            confidence=0.0,
            edge_ratio=0.0,
            net_return=0.0,
            position_size=0.0,
            rejection_reason=RejectionReason.SIGNAL_OUT_OF_BOUNDS,
            signal_validity=SignalValidity.INVALID,  # §12 — component OOB
        )
        return DecisionPipelineResult(decision=decision, vix=None)

    def _invalid_edge_decision(
        self,
        inputs: PipelineInputs,
        artifact: PredictionArtifact,
        signals: SignalComponents,
        regime: str,
    ) -> DecisionPipelineResult:
        decision = Decision(
            decision_id=str(uuid.uuid4()),
            prediction_id=artifact.prediction_id,
            pair=artifact.pair,
            timestamp=utcnow(),
            as_of=artifact.as_of,
            horizon_days=artifact.horizon_days,
            actionable=False,
            direction=Direction.NEUTRAL,
            confidence=0.0,
            edge_ratio=0.0,
            net_return=0.0,
            position_size=0.0,
            rejection_reason=RejectionReason.INVALID_EDGE_THRESHOLD,
            signal_validity=SignalValidity.INVALID,
        )
        return DecisionPipelineResult(
            decision=decision, signals=signals, regime=regime, vix=None
        )