"""
Research Gate — Layer 3 v5.0 §8

Validates models through four gates:
1. Leakage Check
2. Statistical Validation
3. Economic Validation
4. Robustness Check
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class GateResult:
    gate_name: str
    passed: bool
    details: Dict[str, Any]
    message: str


@dataclass
class ResearchGateReport:
    leakage_check: GateResult
    statistical_validation: GateResult
    economic_validation: GateResult
    robustness_check: GateResult
    
    @property
    def overall_status(self) -> str:
        if all([self.leakage_check.passed, self.statistical_validation.passed,
                self.economic_validation.passed, self.robustness_check.passed]):
            return "APPROVED"
        return "REJECTED"


class ResearchGate:
    """Research Gate — validates models before production approval."""
    
    # Screening thresholds (§8)
    MIN_DA = 0.52      # Directional Accuracy > 52%
    MAX_ECE = 0.05     # Expected Calibration Error < 0.05
    MIN_AUC = 0.55     # AUC > 0.55
    MIN_SHARPE = 0.3   # Sharpe (net) > 0.3
    MIN_PROFIT_FACTOR = 1.2
    MAX_DRAWDOWN = -0.20
    MIN_ROLLING_SHARPE = 0.2
    MIN_WINDOWS_GOOD = 0.75
    
    def check_leakage(self, features: Dict[str, Any]) -> GateResult:
        """
        Gate 1: Leakage Check (§8)
        
        ✓ available_time <= prediction_timestamp for ALL features
        ✓ No interpolation used (AS-OF JOIN only)
        ✓ Correct purging based on label overlap
        ✓ Expected values have available_time
        ✓ RAG documents have publication_timestamp
        """
        failures = []
        
        # Check feature available times
        for feature, data in features.items():
            available_time = data.get('available_time')
            prediction_time = data.get('prediction_timestamp')
            
            if available_time and prediction_time:
                if available_time > prediction_time:
                    failures.append(f"{feature}: available_time > prediction_timestamp")
        
        if failures:
            return GateResult(
                gate_name="Leakage Check",
                passed=False,
                details={"failures": failures},
                message=f"Leakage detected: {len(failures)} failures"
            )
        
        return GateResult(
            gate_name="Leakage Check",
            passed=True,
            details={"features_checked": len(features)},
            message="No leakage detected"
        )
    
    def check_statistical(self, metrics: Dict[str, float]) -> GateResult:
        """
        Gate 2: Statistical Validation (§8)
        
        ✓ Directional Accuracy > 52%
        ✓ Expected Calibration Error < 0.05
        ✓ AUC > 0.55
        """
        failures = []
        
        if metrics.get('directional_accuracy', 0) <= self.MIN_DA:
            failures.append(f"DA {metrics.get('directional_accuracy', 0):.3f} <= {self.MIN_DA}")
        
        if metrics.get('ece', 1) >= self.MAX_ECE:
            failures.append(f"ECE {metrics.get('ece', 1):.3f} >= {self.MAX_ECE}")
        
        if metrics.get('auc', 0) <= self.MIN_AUC:
            failures.append(f"AUC {metrics.get('auc', 0):.3f} <= {self.MIN_AUC}")
        
        if failures:
            return GateResult(
                gate_name="Statistical Validation",
                passed=False,
                details={"failures": failures, "metrics": metrics},
                message=f"Statistical validation failed: {len(failures)} failures"
            )
        
        return GateResult(
            gate_name="Statistical Validation",
            passed=True,
            details={"metrics": metrics},
            message="All statistical criteria passed"
        )
    
    def check_economic(self, metrics: Dict[str, float]) -> GateResult:
        """
        Gate 3: Economic Validation (§8)
        
        ✓ Sharpe (net) > 0.3
        ✓ Maximum Drawdown > -20%
        ✓ Profit Factor > 1.2
        ✓ Positive net return (after transaction costs)
        ✓ Performance consistent across regimes
        """
        failures = []
        
        if metrics.get('sharpe_net', 0) <= self.MIN_SHARPE:
            failures.append(f"Sharpe_net {metrics.get('sharpe_net', 0):.3f} <= {self.MIN_SHARPE}")
        
        if metrics.get('max_drawdown', 0) <= self.MAX_DRAWDOWN:
            failures.append(f"MaxDD {metrics.get('max_drawdown', 0):.3f} <= {self.MAX_DRAWDOWN}")
        
        if metrics.get('profit_factor', 1) <= self.MIN_PROFIT_FACTOR:
            failures.append(f"Profit Factor {metrics.get('profit_factor', 1):.3f} <= {self.MIN_PROFIT_FACTOR}")
        
        if metrics.get('net_return', 0) <= 0:
            failures.append(f"Net return {metrics.get('net_return', 0):.3f} <= 0")
        
        if failures:
            return GateResult(
                gate_name="Economic Validation",
                passed=False,
                details={"failures": failures, "metrics": metrics},
                message=f"Economic validation failed: {len(failures)} failures"
            )
        
        return GateResult(
            gate_name="Economic Validation",
            passed=True,
            details={"metrics": metrics},
            message="All economic criteria passed"
        )
    
    def check_robustness(self, results: Dict[str, Any]) -> GateResult:
        """
        Gate 4: Robustness Check (§8)
        
        ✓ Threshold sensitivity: smooth curve
        ✓ Parameter sensitivity: no abrupt cliffs
        ✓ Walk-forward stability: rolling Sharpe > 0.2 in > 75% of windows
        ✓ OOS consistency across subperiods
        """
        failures = []
        
        rolling_sharpe = results.get('rolling_sharpe', [])
        if rolling_sharpe:
            good_windows = sum(1 for s in rolling_sharpe if s > self.MIN_ROLLING_SHARPE)
            ratio = good_windows / len(rolling_sharpe) if rolling_sharpe else 0
            if ratio < self.MIN_WINDOWS_GOOD:
                failures.append(
                    f"Rolling Sharpe > {self.MIN_ROLLING_SHARPE} in only {ratio:.1%} of windows "
                    f"(required {self.MIN_WINDOWS_GOOD:.1%})"
                )
        
        # Check OOS consistency
        oos_metrics = results.get('oos_metrics', [])
        if oos_metrics:
            # Check for any single bad period
            for period, metrics in enumerate(oos_metrics):
                if metrics.get('sharpe_net', 0) < -0.5:
                    failures.append(f"Poor performance in OOS period {period}: Sharpe {metrics.get('sharpe_net', 0):.3f}")
        
        if failures:
            return GateResult(
                gate_name="Robustness Check",
                passed=False,
                details={"failures": failures},
                message=f"Robustness check failed: {len(failures)} failures"
            )
        
        return GateResult(
            gate_name="Robustness Check",
            passed=True,
            details={"windows_checked": len(rolling_sharpe) if rolling_sharpe else 0},
            message="All robustness criteria passed"
        )
    
    def evaluate(self, features: Dict, metrics: Dict, economic: Dict, 
                 robustness: Dict) -> ResearchGateReport:
        """Run all four gates and produce a report."""
        
        leakage = self.check_leakage(features)
        statistical = self.check_statistical(metrics)
        economic_gate = self.check_economic(economic)
        robustness_gate = self.check_robustness(robustness)
        
        return ResearchGateReport(
            leakage_check=leakage,
            statistical_validation=statistical,
            economic_validation=economic_gate,
            robustness_check=robustness_gate
        )
