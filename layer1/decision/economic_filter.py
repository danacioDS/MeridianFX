"""
Economic Filter — Transforma forecast en decisión económica.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Forecast:
    direction: str  # UP / DOWN
    probability: float
    expected_return: float
    expected_volatility: float


@dataclass
class Costs:
    spread: float = 0.0010      # 10 bps
    slippage: float = 0.0005    # 5 bps
    fees: float = 0.0005        # 5 bps


@dataclass
class EconomicFilterResult:
    gross_return: float
    spread_cost: float
    slippage_cost: float
    fees: float
    net_return: float
    edge_ratio: float
    minimum_edge: float
    actionable: bool
    position_size: float


class EconomicFilter:
    """
    Aplica el filtro económico a un forecast.
    
    Convierte un forecast bruto en una decisión económica
    considerando costos de transacción.
    """
    
    def __init__(self, minimum_edge: float = 1.5):
        self.minimum_edge = minimum_edge
        self.costs = Costs()
    
    def apply(self, forecast: Forecast) -> EconomicFilterResult:
        """
        Aplica el filtro económico.
        
        Args:
            forecast: Predicción del modelo
            
        Returns:
            EconomicFilterResult con retorno neto y decisión
        """
        gross_return = forecast.expected_return
        
        # Costos
        spread_cost = self.costs.spread * abs(gross_return) if gross_return > 0 else self.costs.spread * 0.5
        slippage_cost = self.costs.slippage * abs(gross_return) if gross_return > 0 else self.costs.slippage * 0.5
        fees = self.costs.fees
        
        # Retorno neto
        net_return = gross_return - spread_cost - slippage_cost - fees
        
        # Edge Ratio: retorno neto / volatilidad
        edge_ratio = abs(net_return) / forecast.expected_volatility if forecast.expected_volatility > 0 else 0
        
        # Decisión
        actionable = edge_ratio >= self.minimum_edge and net_return > 0
        
        # Tamaño de posición (simplificado)
        position_size = min(
            edge_ratio / (self.minimum_edge * 2),
            0.05  # máximo 5%
        ) if actionable else 0
        
        return EconomicFilterResult(
            gross_return=gross_return,
            spread_cost=spread_cost,
            slippage_cost=slippage_cost,
            fees=fees,
            net_return=net_return,
            edge_ratio=edge_ratio,
            minimum_edge=self.minimum_edge,
            actionable=actionable,
            position_size=position_size
        )
