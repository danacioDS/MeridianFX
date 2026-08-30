"""
PIT Adversarial Tests — Layer 4 v3.1.1 §7

Test datasets A-D:
- Dataset A: Normal (must PASS)
- Dataset B: Leakage (must FAIL PIT-1)
- Dataset C: Revision Leakage (must select V1)
- Dataset D: Derived Leakage (must FAIL PIT-2)
"""
import pytest
from datetime import datetime, timedelta
import pytz
from layer4.quality.pit_validator import PITValidator, PITValidationReport


class TestPITAdversarial:
    """Adversarial tests for PIT validation."""
    
    @pytest.fixture
    def validator(self):
        return PITValidator()
    
    @pytest.fixture
    def t0(self):
        """Reference timestamp T."""
        return pytz.UTC.localize(datetime(2026, 8, 30, 12, 0, 0))
    
    def test_dataset_a_normal(self, validator, t0):
        """
        Dataset A — Normal
        Correctly timestamped features, correctly constructed targets.
        Must PASS all PIT invariants.
        """
        feature = {
            'feature_id': 'us_10y_yield',
            'available_time': t0 - timedelta(hours=2),
            'is_interpolated': False,
            'target_start': t0 + timedelta(days=1),
            'target_end': t0 + timedelta(days=6),
            'event_time': t0 - timedelta(days=1),
            'release_time': t0 - timedelta(hours=3),
            'source_available_time': t0 - timedelta(hours=2),
            'system_available_time': t0 - timedelta(hours=1),
        }
        
        report = validator.validate(feature, t0)
        assert report.passed, f"Dataset A failed: {[f for f in report.failures]}"
        assert len(report.failures) == 0
    
    def test_dataset_b_leakage(self, validator, t0):
        """
        Dataset B — Leakage
        available_time > prediction_timestamp
        Must FAIL PIT-1.
        """
        feature = {
            'feature_id': 'us_10y_yield',
            'available_time': t0 + timedelta(hours=2),  # Leakage
            'is_interpolated': False,
        }
        
        report = validator.validate(feature, t0)
        assert not report.passed
        pit1_failures = [r for r in report.failures if r.invariant == 'PIT-1']
        assert len(pit1_failures) > 0, "Expected PIT-1 failure for leakage"
    
    def test_dataset_c_revision_leakage(self, validator, t0):
        """
        Dataset C — Revision Leakage
        V1 available at T, V2 available after T
        Must select V1 (latest valid vintage)
        """
        vintages = [
            {
                'vintage_id': 'V1',
                'vintage_time': t0 - timedelta(days=5),
                'available_time': t0 - timedelta(days=1),
            },
            {
                'vintage_id': 'V2',
                'vintage_time': t0 - timedelta(days=3),
                'available_time': t0 + timedelta(days=1),  # After T
            },
        ]
        
        result = validator.check_vintage_selection(vintages, t0, selected_vintage_id='V1')
        assert result.passed, "Should select V1 (latest valid vintage)"
        assert 'V1' in result.message, f"Expected V1, got {result.message}"
    
    def test_dataset_d_derived_leakage(self, validator, t0):
        """
        Dataset D — Derived Leakage
        derived.available_time != max(inputs.available_time)
        Must FAIL PIT-2.
        """
        inputs = [
            {'available_time': t0 - timedelta(hours=2)},
            {'available_time': t0 - timedelta(hours=1)},
        ]
        
        derived = {
            'available_time': t0 - timedelta(hours=3),  # Incorrect
        }
        
        result = validator.check_derived_propagation(derived, inputs)
        assert not result.passed, "Expected PIT-2 failure for derived leakage"
        assert result.invariant == 'PIT-2'
