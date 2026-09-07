"""
Canonical Macro Adapter.

Convierte la taxonomía producida por MacroTransformer
en la taxonomía consumida por PredictionArtifact / DecisionPipeline.

Este módulo NO calcula nuevos indicadores económicos.
Únicamente normaliza semántica entre contratos.
"""

from typing import Dict


class CanonicalMacroAdapter:
    """Adapta el régimen macro de Layer 2 al contrato canónico."""

    @staticmethod
    def to_canonical(regime: Dict[str, str]) -> Dict[str, str]:
        """
        Convierte MacroTransformer.to_regime() a MacroRegime canónico.

        La dimensión `risk` se trata conservadoramente:
        MacroTransformer usa Fed Funds como proxy monetario, no como
        una medida real de Risk-On / Risk-Off.

        Por ello:
          MODERATE -> Neutral
          RESTRICTIVE / ACCOMMODATIVE -> UNKNOWN

        UNKNOWN se conserva como UNKNOWN cuando no existe información
        semánticamente válida.
        """

        risk_map = {
            "MODERATE": "Neutral",
            "UNKNOWN": "UNKNOWN",
        }

        policy_map = {
            "RESTRICTIVE": "Restrictive",
            "NEUTRAL": "Neutral",
            "ACCOMMODATIVE": "Accommodative",
            "UNKNOWN": "UNKNOWN",
        }

        growth_map = {
            "STRONG": "High",
            "STABLE": "Moderate",
            "WEAK": "Low",
            "UNKNOWN": "UNKNOWN",
        }

        inflation_map = {
            "HIGH": "High",
            "MODERATE": "Moderate",
            "LOW": "Low",
            "UNKNOWN": "UNKNOWN",
        }

        return {
            "risk": risk_map.get(
                regime.get("risk", "UNKNOWN"),
                "UNKNOWN",
            ),
            "policy": policy_map.get(
                regime.get("policy", "UNKNOWN"),
                "UNKNOWN",
            ),
            "growth": growth_map.get(
                regime.get("growth", "UNKNOWN"),
                "UNKNOWN",
            ),
            "inflation": inflation_map.get(
                regime.get("inflation", "UNKNOWN"),
                "UNKNOWN",
            ),
        }
