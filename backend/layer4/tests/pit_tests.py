"""
PIT Tests — Layer 4 v3.1.1 §4

5 test groups for PIT validation.
"""
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any
from ..quality.pit_validator import PITValidator, ValidationResult


class PITTestRunner:
    """
    Run PIT tests (T1-T5).
    
    T1: Feature Availability (PIT-1, PIT-5)
    T2: Vintage Selection (PIT-3, PIT-5)
    T3: PIT Propagation (PIT-2)
    T4: Target Timing (PIT-6)
    T5: No Interpolation (PIT-4)
    """
    
    def __init__(self):
        self.validator = PITValidator()
        self.results = []
    
    def _utc(self, dt: datetime) -> datetime:
        """Ensure UTC timezone."""
        if dt.tzinfo is None:
            return pytz.UTC.localize(dt)
        return dt.astimezone(pytz.UTC)
    
    def test_t1_feature_availability(self, feature: Dict[str, Any],
                                     prediction_timestamp: datetime) -> bool:
        """
        T1: Feature Availability
        Invariants: PIT-1, PIT-5
        Failure: available_time > prediction_timestamp
        """
        result = self.validator.check_available_time(feature, prediction_timestamp)
        self.results.append(result)
        return result.passed
    
    def test_t2_vintage_selection(self, vintages: List[Dict[str, Any]],
                                  prediction_timestamp: datetime) -> bool:
        """
        T2: Vintage Selection
        Invariants: PIT-3, PIT-5
        Failure: vintage_time > prediction_timestamp
        """
        result = self.validator.check_vintage_selection(vintages, prediction_timestamp)
        self.results.append(result)
        return result.passed
    
    def test_t3_pit_propagation(self, derived: Dict[str, Any],
                                inputs: List[Dict[str, Any]]) -> bool:
        """
        T3: PIT Propagation
        Invariants: PIT-2
        Failure: derived.available_time != max(inputs.available_time)
        """
        result = self.validator.check_derived_propagation(derived, inputs)
        self.results.append(result)
        return result.passed
    
    def test_t4_target_timing(self, prediction_timestamp: datetime,
                              target_start: datetime, target_end: datetime) -> bool:
        """
        T4: Target Timing
        Invariants: PIT-6
        Failure: prediction_timestamp >= target_start or target_start >= target_end
        """
        result = self.validator.check_target_timing(
            prediction_timestamp, target_start, target_end
        )
        self.results.append(result)
        return result.passed
    
    def test_t5_no_interpolation(self, feature: Dict[str, Any]) -> bool:
        """
        T5: No Interpolation
        Invariants: PIT-4
        Failure: is_interpolated = True
        """
        result = self.validator.check_no_interpolation(feature)
        self.results.append(result)
        return result.passed
    
    def run_all(self, feature: Dict[str, Any], 
        """Run all 5 tests on a feature."""
        results = {
            "T1": self.test_t1_feature_availability(feature, prediction_timestamp),
            "T5": self.test_t5_no_interpolation(feature),
        }
        
        if "vintages" in feature:
            results["T2"] = self.test_t2_vintage_selection(
                feature["vintages"], prediction_timestamp
            )
        
        if "target_start" in feature and "target_end" in feature:
            results["T4"] = self.test_t4_target_timing(
                prediction_timestamp,
                feature["target_start"],
                feature["target_end"]
            )
        
        # T3: PIT Propagation (requires inputs)
        if "inputs" in feature and "derived" in feature:
            results["T3"] = self.test_t3_pit_propagation(
                feature["derived"],
                feature["inputs"]
            )
        
        return results
    
    def run_all_with_t3(self, feature: Dict[str, Any],
                        prediction_timestamp: datetime,
                        derived: Dict[str, Any],
                        inputs: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Run all 5 tests including T3."""
        results = self.run_all(feature, prediction_timestamp)
        results["T3"] = self.test_t3_pit_propagation(derived, inputs)
        return results/g
                prediction_timestamp: datetime) -> Dict[str, bool]:
        """Run all 5 tests on a feature."""
        results = {
            'T1': self.test_t1_feature_availability(feature, prediction_timestamp),
            'T5': self.test_t5_no_interpolation(feature),
        }
        
        if 'vintages' in feature:
            results['T2'] = self.test_t2_vintage_selection(
                feature['vintages'], prediction_timestamp
            )
        
        if 'target_start' in feature and 'target_end' in feature:
            results['T4'] = self.test_t4_target_timing(
                prediction_timestamp,
                feature['target_start'],
                feature['target_end']
            )
        
        return results
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of all test results."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        return {
            'passed': passed,
            'total': total,
            'passed_pct': (passed / total * 100) if total > 0 else 0,
            'results': [{'invariant': r.invariant, 'passed': r.passed, 
                        'message': r.message} for r in self.results]
        }
