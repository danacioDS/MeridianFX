"""Prompt 1 — §3 signals, §5 fusion, §6 confidence formulas."""

from __future__ import annotations

import pytest

from meridian_fx.decision.contracts import (
    ConfidenceCalculator,
    Direction,
    FusionEngine,
    NEUTRAL_THRESHOLD,
    Regime,
    SignalComponents,
    SignalGenerator,
    SignalOutOfBoundsError,
    compute_regime_alignment,
    determine_regime,
)
from meridian_fx.decision.contracts.signal import raw_macro_score, raw_rag_score


class TestSignalGenerator:
    def test_quant_score(self):
        assert SignalGenerator.quant_score(0.65) == pytest.approx(0.30)

    def test_quant_score_bounds(self):
        with pytest.raises(ValueError):
            SignalGenerator.quant_score(1.5)

    def test_macro_score_formula(self):
        score = SignalGenerator.macro_score(0.4, 0.2, 0.2)
        assert score == pytest.approx(0.50 * 0.4 + 0.25 * 0.2 + 0.25 * 0.2)

    def test_rag_score_formula(self):
        assert SignalGenerator.rag_score(0.2, -0.1) == pytest.approx(0.15)

    def test_generate_fills_missing_components(self):
        gen = SignalGenerator()
        components = gen.generate(
            probability_up=0.65,
            policy_differential=0.4,
            growth_differential=0.2,
            normalized_rate_differential=0.2,
            base_signal=0.2,
            quote_signal=-0.1,
        )
        assert components.quant_score.value == pytest.approx(0.30)
        assert components.macro_score.value == pytest.approx(0.30)
        assert components.rag_score.value == pytest.approx(0.15)

    def test_out_of_bounds_raises(self):
        gen = SignalGenerator()
        with pytest.raises(SignalOutOfBoundsError):
            gen.generate(probability_up=0.9, policy_differential=0.4, growth_differential=2.0, normalized_rate_differential=2.0, base_signal=0.2, quote_signal=-0.1)


class TestFusionEngine:
    def test_weights_sum_to_one_for_all_regimes(self):
        from meridian_fx.decision.contracts import FUSION_WEIGHTS

        for regime, weights in FUSION_WEIGHTS.items():
            assert weights.sum() == pytest.approx(1.0), f"regime {regime}"

    def test_expansion_fusion(self):
        signals = SignalComponents(quant_score=0.30, macro_score=0.30, rag_score=0.15)
        result = FusionEngine().fuse(signals, Regime.EXPANSION)
        assert result.fusion_score == pytest.approx(0.5 * 0.30 + 0.3 * 0.30 + 0.2 * 0.15)
        assert result.direction == Direction.LONG
        assert result.direction_sign == 1

    def test_neutral_threshold_strict(self):
        engine = FusionEngine()
        signals = SignalComponents(quant_score=0.10, macro_score=0.10, rag_score=0.10)
        result = engine.fuse(signals, "UNKNOWN")  # 0.5*0.1+0.3*0.1+0.2*0.1 = 0.10
        assert result.fusion_score == pytest.approx(NEUTRAL_THRESHOLD)
        assert result.direction == Direction.NEUTRAL  # ±0.10 → NEUTRAL (strict)

    def test_direction_long_short(self):
        long_s = SignalComponents(quant_score=0.5, macro_score=0.5, rag_score=0.5)
        assert FusionEngine().fuse(long_s, Regime.EXPANSION).direction == Direction.LONG
        short_s = SignalComponents(quant_score=-0.5, macro_score=-0.5, rag_score=-0.5)
        assert FusionEngine().fuse(short_s, Regime.EXPANSION).direction == Direction.SHORT

    def test_unknown_regime_lookup_raises(self):
        with pytest.raises(ValueError):
            FusionEngine().fuse(SignalComponents(quant_score=0.1, macro_score=0.1, rag_score=0.1), "Nope")


class TestConfidence:
    def test_formula(self):
        calc = ConfidenceCalculator()
        result = calc.compute(
            fusion_score=0.27,
            quant_score=0.3,
            macro_score=0.3,
            rag_score=0.15,
            model_confidence=0.9,
            historical_reliability=0.5,
        )
        assert result.confidence == pytest.approx(
            0.4 * 0.27 + 0.3 * 0.9 + 0.2 * 0.5 + 0.1 * 0.925
        )

    def test_model_confidence_interval(self):
        calc = ConfidenceCalculator()
        assert calc.model_confidence_from_interval(width=0.1, p5_width=0.0, p95_width=1.0) == pytest.approx(0.9)
        assert calc.model_confidence_from_interval(width=0.5, p5_width=0.5, p95_width=0.5) == 0.5
        assert calc.model_confidence_from_interval(width=2.0, p5_width=0.0, p95_width=1.0) == 0.0  # clipped

    def test_cross_signal_agreement(self):
        calc = ConfidenceCalculator()
        assert calc.cross_signal_agreement([0.3, 0.3, 0.15]) == pytest.approx(1 - (0.3 - 0.15) / 2)


class TestRegimeAlignment:
    def test_alignment_formula(self):
        alignment = compute_regime_alignment("Risk-On", "Neutral", "Neutral", "LONG")
        assert alignment == pytest.approx(0.30 * 1.00 + 0.35 * 0.75 + 0.35 * 0.75)

    def test_risk_off_short_preferred(self):
        alignment = compute_regime_alignment("Risk-Off", "Accommodative", "Accommodative", "SHORT")
        assert alignment > compute_regime_alignment("Risk-Off", "Accommodative", "Accommodative", "LONG")

    def test_direction_determination_regime(self):
        assert determine_regime({"risk": "Risk-On", "policy": "Neutral", "growth": "High", "inflation": "Low"}) == "Goldilocks"
        assert determine_regime({}) == "UNKNOWN"