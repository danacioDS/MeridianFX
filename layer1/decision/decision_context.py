"""
Decision Context — Contexto completo para la interpretación LLM.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from .economic_filter import EconomicFilterResult, Forecast
from .signal_validity import SignalValidity


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
    
    # Comparativas (opcional)
    previous_probability: Optional[float] = None
    previous_edge: Optional[float] = None
    previous_regime: Optional[str] = None
    
    # Metadatos
    timestamp: datetime = field(default_factory=datetime.now)
    model_version: str = "xgb-v1.0"
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para el LLM"""
        return {
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
            } if self.previous_probability else None,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat(),
        }


class DecisionEngine:
    """
    Motor de decisión que integra forecast, filtro económico y validez.
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
    ) -> DecisionContext:
        """
        Construye el contexto de decisión completo.
        
        Args:
            pair: Par de divisas
            direction: Dirección (UP/DOWN)
            probability: Probabilidad
            expected_return: Retorno esperado
            expected_volatility: Volatilidad esperada
            regime: Régimen de riesgo
            vix: Índice VIX
            yield_spread: Diferencial de rendimientos
            policy_divergence: Divergencia de política
            horizon: Horizonte de forecast
            previous_probability: Probabilidad anterior
            previous_edge: Edge anterior
            previous_regime: Régimen anterior
            
        Returns:
            DecisionContext completo
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
        
        # 3. Construir contexto
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
            previous_probability=previous_probability,
            previous_edge=previous_edge,
            previous_regime=previous_regime,
            model_version="xgb-v1.0"
        )
