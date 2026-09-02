"""
Signal Validity — Condiciones que mantienen o invalidan la tesis.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SignalValidity:
    """Condiciones de validez de la señal"""
    
    # Condiciones que mantienen la tesis
    thesis_conditions: List[str]
    
    # Condiciones que invalidan la tesis
    invalidation_conditions: List[str]
    
    # Estado actual de la tesis
    thesis_valid: bool = True
    
    # Razón de invalidez (si aplica)
    invalidation_reason: Optional[str] = None


class SignalValidityEngine:
    """
    Evalúa las condiciones que mantienen o invalidan la tesis.
    """
    
    def __init__(self):
        self.default_conditions = {
            "thesis": [
                "Yield spread US-JP > 2.5%",
                "VIX < 22",
                "Policy divergence persists"
            ],
            "invalidation": [
                "Yield spread reverses materially",
                "Regime changes to Risk-Off",
                "Unexpected BoJ intervention"
            ]
        }
    
    def evaluate(
        self,
        direction: str,
        regime: str,
        yield_spread: float,
        vix: float,
        policy_divergence: str
    ) -> SignalValidity:
        """
        Evalúa la validez de la señal.
        
        Args:
            direction: Dirección de la señal (UP/DOWN)
            regime: Régimen de riesgo (RISK_ON/RISK_OFF)
            yield_spread: Diferencial de rendimientos
            vix: Índice VIX
            policy_divergence: Divergencia de política
            
        Returns:
            SignalValidity con condiciones y estado
        """
        # Condiciones para mantener la tesis
        thesis_conditions = []
        
        if yield_spread > 2.5:
            thesis_conditions.append(f"Yield spread US-JP > 2.5% (actual: {yield_spread:.2f}%)")
        else:
            thesis_conditions.append(f"Yield spread US-JP {yield_spread:.2f}% (umbral: 2.5%)")
        
        if vix < 22:
            thesis_conditions.append(f"VIX < 22 (actual: {vix:.1f})")
        else:
            thesis_conditions.append(f"VIX {vix:.1f} (umbral: 22)")
        
        if policy_divergence.upper() in ["HIGH", "INCREASED"]:
            thesis_conditions.append(f"Policy divergence persists ({policy_divergence})")
        else:
            thesis_conditions.append(f"Policy divergence: {policy_divergence}")
        
        # Condiciones de invalidez
        invalidation_conditions = [
            "Yield spread reverses materially",
            "Regime changes to Risk-Off",
            "Unexpected BoJ intervention"
        ]
        
        # Evaluar si la tesis es válida
        thesis_valid = True
        invalidation_reason = None
        
        # Riesgo de invalidez
        if regime.upper() == "RISK_OFF" and direction == "UP":
            thesis_valid = False
            invalidation_reason = "Risk-Off regime is not favorable for bullish positions"
        elif yield_spread < 1.5:
            thesis_valid = False
            invalidation_reason = f"Yield spread too low ({yield_spread:.2f}%)"
        
        return SignalValidity(
            thesis_conditions=thesis_conditions,
            invalidation_conditions=invalidation_conditions,
            thesis_valid=thesis_valid,
            invalidation_reason=invalidation_reason
        )
