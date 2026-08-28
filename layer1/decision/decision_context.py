"""
Decision Context — Contexto completo para la interpretación LLM.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .economic_filter import EconomicFilterResult, Forecast
from .signal_validity import SignalValidity


@dataclass
class MacroContext:
    """Contexto macroeconómico."""
    timestamp: str
    source: str
    summary: Dict[str, Any]
    indicators: Dict[str, Any]
    fx_relevance: str
    series: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "summary": self.summary,
            "indicators": self.indicators,
            "fx_relevance": self.fx_relevance,
        }


@dataclass
class DecisionContext:
    """Contexto completo de decisión para el LLM"""
    
    # Forecast
    pair: str
    direction: str
    probability: float
    horizon: str
    
    # Economic Filter
    economic_filter: EconomicFilterResult
    
    # Signal Validity
    signal_validity: SignalValidity
    
    # Contexto Macro
    regime: str
    vix: float
    yield_spread: float
    policy_divergence: str
    
    # Macro Context (de FRED)
    macro: Optional[MacroContext] = None
    
    # Comparativas (opcional)
    previous_probability: Optional[float] = None
    previous_edge: Optional[float] = None
    previous_regime: Optional[str] = None
    
    # Metadatos
    timestamp: datetime = field(default_factory=datetime.now)
    model_version: str = "xgb-v1.0"
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para el LLM"""
        result = {
            "pair": self.pair,
            "horizon": self.horizon,
            "direction": self.direction,
            "probability": self.probability,
            "economic_filter": {
                "gross_return": self.economic_filter.gross_return,
                "spread_cost": self.economic_filter.spread_cost,
                "slippage_cost": self.economic_filter.slippage_cost,
                "fees": self.economic_filter.fees,
                "net_return": self.economic_filter.net_return,
                "edge_ratio": self.economic_filter.edge_ratio,
                "minimum_edge": self.economic_filter.minimum_edge,
                "actionable": self.economic_filter.actionable,
                "position_size": self.economic_filter.position_size,
            },
            "regime": self.regime,
            "vix": self.vix,
            "yield_spread": self.yield_spread,
            "policy_divergence": self.policy_divergence,
            "signal_validity": {
                "thesis_conditions": self.signal_validity.thesis_conditions,
                "invalidation_conditions": self.signal_validity.invalidation_conditions,
                "thesis_valid": self.signal_validity.thesis_valid,
                "invalidation_reason": self.signal_validity.invalidation_reason,
            },
            "previous": {
                "probability": self.previous_probability,
                "edge": self.previous_edge,
                "regime": self.previous_regime,
            } if self.previous_probability is not None else None,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat(),
        }
        
        # Añadir macro si está disponible
        if self.macro:
            result["macro"] = self.macro.to_dict()
        
        return result


class DecisionEngine:
    """
    Motor de decisión que integra forecast, filtro económico, validez y macro.
    """
    
    def __init__(self):
        from .economic_filter import EconomicFilter
        from .signal_validity import SignalValidityEngine
        
        self.economic_filter = EconomicFilter()
        self.signal_validity = SignalValidityEngine()
    
    def build_context(
        self,
        pair: str,
        direction: str,
        probability: float,
        expected_return: float,
        expected_volatility: float,
        regime: str,
        vix: float,
        yield_spread: float,
        policy_divergence: str,
        horizon: str = "5D",
        previous_probability: Optional[float] = None,
        previous_edge: Optional[float] = None,
        previous_regime: Optional[str] = None,
        macro_context: Optional[Dict] = None,
    ) -> DecisionContext:
        """
        Construye el contexto de decisión completo.
        """
        # 1. Aplicar filtro económico
        forecast = Forecast(
            direction=direction,
            probability=probability,
            expected_return=expected_return,
            expected_volatility=expected_volatility
        )
        economic_filter_result = self.economic_filter.apply(forecast)
        
        # 2. Evaluar validez
        signal_validity = self.signal_validity.evaluate(
            direction=direction,
            regime=regime,
            yield_spread=yield_spread,
            vix=vix,
            policy_divergence=policy_divergence
        )
        
        # 3. Crear MacroContext si hay datos
        macro = None
        if macro_context:
            macro = MacroContext(
                timestamp=macro_context.get("timestamp", datetime.now().isoformat()),
                source=macro_context.get("source", "FRED"),
                summary=macro_context.get("summary", {}),
                indicators=macro_context.get("indicators", {}),
                fx_relevance=macro_context.get("fx_relevance", "UNKNOWN"),
                series=macro_context.get("series", {})
            )
        
        # 4. Construir contexto
        return DecisionContext(
            pair=pair,
            direction=direction,
            probability=probability,
            horizon=horizon,
            economic_filter=economic_filter_result,
            signal_validity=signal_validity,
            regime=regime,
            vix=vix,
            yield_spread=yield_spread,
            policy_divergence=policy_divergence,
            macro=macro,
            previous_probability=previous_probability,
            previous_edge=previous_edge,
            previous_regime=previous_regime,
            model_version="xgb-v1.0"
        )
