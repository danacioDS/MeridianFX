"""
Macro Regime Engine — Layer 3 v5.0 §5.1

Classifies macroeconomic regimes based on:
- Risk: Risk-On / Neutral / Risk-Off
- Policy: Restrictive / Neutral / Accommodative
- Growth: Strong / Moderate / Weak
- Inflation: High / Moderate / Low

Expansion: Risk-On + Accommodative + Strong + Moderate
Late Cycle: Risk-On + Restrictive + Moderate + High
Stagflation: Risk-Off + Restrictive + Weak + High
Recovery: Risk-On + Accommodative + Weak + Low
Crisis: Risk-Off + Accommodative + Weak + Low
"""
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple


@dataclass
class MacroRegime:
    """Macro regime classification."""
    risk: str          # "Risk-On" | "Neutral" | "Risk-Off"
    policy: str        # "Restrictive" | "Neutral" | "Accommodative"
    growth: str        # "Strong" | "Moderate" | "Weak"
    inflation: str     # "High" | "Moderate" | "Low"
    
    @property
    def name(self) -> str:
        """Get the regime name based on combination."""
        if self.risk == "Risk-On" and self.policy == "Accommodative" and self.growth == "Strong" and self.inflation == "Moderate":
            return "Expansion"
        elif self.risk == "Risk-On" and self.policy == "Restrictive" and self.growth == "Moderate" and self.inflation == "High":
            return "Late Cycle"
        elif self.risk == "Risk-Off" and self.policy == "Restrictive" and self.growth == "Weak" and self.inflation == "High":
            return "Stagflation"
        elif self.risk == "Risk-On" and self.policy == "Accommodative" and self.growth == "Weak" and self.inflation == "Low":
            return "Recovery"
        elif self.risk == "Risk-Off" and self.policy == "Accommodative" and self.growth == "Weak" and self.inflation == "Low":
            return "Crisis"
        return "Mixed"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'risk': self.risk,
            'policy': self.policy,
            'growth': self.growth,
            'inflation': self.inflation,
            'regime': self.name
        }


class MacroRegimeEngine:
    """
    Macro Regime Engine — classifies regimes from macro indicators.
    """
    
    def __init__(self):
        self.indicators = {}
    
    def _classify_risk(self, vix: float, credit_spread: float) -> str:
        """Classify risk regime from VIX and credit spreads."""
        if vix < 18 and credit_spread < 1.5:
            return "Risk-On"
        elif vix > 25 and credit_spread > 2.5:
            return "Risk-Off"
        return "Neutral"
    
    def _classify_policy(self, fed_funds: float, inflation: float, 
                         neutral_rate: float = 2.5) -> str:
        """Classify policy regime from fed funds rate."""
        real_rate = fed_funds - inflation
        if real_rate > neutral_rate + 0.5:
            return "Restrictive"
        elif real_rate < neutral_rate - 0.5:
            return "Accommodative"
        return "Neutral"
    
    def _classify_growth(self, gdp_growth: float, pmi: float) -> str:
        """Classify growth regime from GDP and PMI."""
        if gdp_growth > 2.5 and pmi > 55:
            return "Strong"
        elif gdp_growth < 1.0 and pmi < 45:
            return "Weak"
        return "Moderate"
    
    def _classify_inflation(self, cpi: float, core_cpi: float) -> str:
        """Classify inflation regime from CPI."""
        avg_inflation = (cpi + core_cpi) / 2
        if avg_inflation > 3.0:
            return "High"
        elif avg_inflation < 1.5:
            return "Low"
        return "Moderate"
    
    def classify(self, indicators: Dict[str, float]) -> MacroRegime:
        """
        Classify macro regime from indicators.
        
        Expected indicators:
        - vix: float
        - credit_spread: float (10Y-2Y spread)
        - fed_funds: float
        - inflation: float (CPI)
        - core_inflation: float (Core CPI)
        - gdp_growth: float
        - pmi: float
        """
        # Extract indicators with defaults
        vix = indicators.get('vix', 20.0)
        credit_spread = indicators.get('credit_spread', 1.0)
        fed_funds = indicators.get('fed_funds', 2.5)
        inflation = indicators.get('inflation', 2.0)
        core_inflation = indicators.get('core_inflation', 2.0)
        gdp_growth = indicators.get('gdp_growth', 2.0)
        pmi = indicators.get('pmi', 50.0)
        
        risk = self._classify_risk(vix, credit_spread)
        policy = self._classify_policy(fed_funds, inflation)
        growth = self._classify_growth(gdp_growth, pmi)
        inflation_regime = self._classify_inflation(inflation, core_inflation)
        
        return MacroRegime(
            risk=risk,
            policy=policy,
            growth=growth,
            inflation=inflation_regime
        )
    
    def get_regime_features(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """
        Get regime features for model input.
        
        Converts regime classifications to numerical features.
        """
        regime = self.classify(indicators)
        
        # One-hot encode regimes
        risk_map = {"Risk-On": 1.0, "Neutral": 0.0, "Risk-Off": -1.0}
        policy_map = {"Accommodative": 1.0, "Neutral": 0.0, "Restrictive": -1.0}
        growth_map = {"Strong": 1.0, "Moderate": 0.0, "Weak": -1.0}
        inflation_map = {"Low": -1.0, "Moderate": 0.0, "High": 1.0}
        
        return {
            'regime_risk': risk_map.get(regime.risk, 0.0),
            'regime_policy': policy_map.get(regime.policy, 0.0),
            'regime_growth': growth_map.get(regime.growth, 0.0),
            'regime_inflation': inflation_map.get(regime.inflation, 0.0),
            'regime_name': 0.0,  # For compatibility
            'regime_score': 0.0   # For compatibility
        }
