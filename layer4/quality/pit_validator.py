"""
PIT Validator — Layer 4 v3.1.1 §2, §3

Validates that all features respect Point-in-Time invariants.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import pytz


@dataclass
class ValidationResult:
    """Result of a PIT validation."""
    passed: bool
    invariant: str
    message: str
    details: Dict[str, Any]


@dataclass
class PITValidationReport:
    """Complete PIT validation report."""
    feature_id: str
    prediction_timestamp: datetime
    results: List[ValidationResult]
    
    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)
    
    @property
    def failures(self) -> List[ValidationResult]:
        return [r for r in self.results if not r.passed]


class PITValidator:
    """
    PIT Validator — validates all 7 invariants.
    
    PIT-1: available_time <= T
    PIT-2: derived.available_time = max(inputs.available_time)
    PIT-3: vintage_selection = max(vintage_time) WHERE available_time <= T
    PIT-4: NO interpolation (AS-OF JOIN only)
    PIT-5: All timestamps timezone-aware (UTC)
    PIT-6: prediction_timestamp < target_start < target_end
    PIT-7: event_time <= release_time <= source_available_time <= system_available_time
    """
    
    def __init__(self):
        self.results = []
    
    def _ensure_utc(self, dt: datetime) -> datetime:
        """PIT-5: Ensure timestamp is timezone-aware UTC."""
        if dt.tzinfo is None:
            return pytz.UTC.localize(dt)
        return dt.astimezone(pytz.UTC)
    
    def check_available_time(self, feature: Dict[str, Any], 
                             prediction_timestamp: datetime) -> ValidationResult:
        """PIT-1: available_time <= T."""
        available_time = feature.get('available_time')
        if available_time is None:
            return ValidationResult(
                passed=False,
                invariant='PIT-1',
                message='available_time is None',
                details={'feature': feature}
            )
        
        available_time = self._ensure_utc(available_time)
        prediction_timestamp = self._ensure_utc(prediction_timestamp)
        
        passed = available_time <= prediction_timestamp
        return ValidationResult(
            passed=passed,
            invariant='PIT-1',
            message=f'available_time {available_time} <= {prediction_timestamp}' if passed 
                    else f'available_time {available_time} > {prediction_timestamp}',
            details={'available_time': available_time.isoformat(),
                    'prediction_timestamp': prediction_timestamp.isoformat()}
        )
    
    def check_derived_propagation(self, derived: Dict[str, Any],
                                   inputs: List[Dict[str, Any]]) -> ValidationResult:
        """PIT-2: derived.available_time = max(inputs.available_time)."""
        derived_time = derived.get('available_time')
        if derived_time is None:
            return ValidationResult(
                passed=False,
                invariant='PIT-2',
                message='derived available_time is None',
                details={}
            )
        
        derived_time = self._ensure_utc(derived_time)
        
        input_times = [self._ensure_utc(i.get('available_time')) 
                      for i in inputs if i.get('available_time') is not None]
        
        if not input_times:
            return ValidationResult(
                passed=False,
                invariant='PIT-2',
                message='No input available_times found',
                details={}
            )
        
        max_input_time = max(input_times)
        passed = derived_time == max_input_time
        
        return ValidationResult(
            passed=passed,
            invariant='PIT-2',
            message=f'derived_time {derived_time} == max_input {max_input_time}' if passed
                    else f'derived_time {derived_time} != max_input {max_input_time}',
            details={'derived_time': derived_time.isoformat(),
                    'max_input_time': max_input_time.isoformat()}
        )
    
    def check_vintage_selection(self, vintages: List[Dict[str, Any]],
                                prediction_timestamp: datetime,
                                selected_vintage_id: Optional[str] = None) -> ValidationResult:
        """
        PIT-3: vintage_selection = max(vintage_time) WHERE available_time <= T.
        
        If selected_vintage_id is provided, verifies that the selected vintage
        is the latest valid vintage (detects revision leakage).
        """
        prediction_timestamp = self._ensure_utc(prediction_timestamp)
        
        # Find all available vintages (available_time <= T)
        available_vintages = []
        vintage_by_id = {}
        
        for v in vintages:
            vintage_id = v.get('vintage_id', 'unknown')
            vintage_by_id[vintage_id] = v
            
            available_time = v.get('available_time')
            if available_time is None:
                continue
            
            available_time = self._ensure_utc(available_time)
            if available_time <= prediction_timestamp:
                vintage_time = v.get('vintage_time')
                if vintage_time is not None:
                    vintage_time = self._ensure_utc(vintage_time)
                    available_vintages.append((vintage_time, vintage_id, v))
        
        if not available_vintages:
            return ValidationResult(
                passed=False,
                invariant='PIT-3',
                message='No vintages available at prediction_timestamp',
                details={'prediction_timestamp': prediction_timestamp.isoformat()}
            )
        
        # The latest valid vintage (by vintage_time)
        latest_vintage = max(available_vintages, key=lambda x: x[0])
        expected_vintage_id = latest_vintage[1]
        
        # If selected_vintage_id is provided, verify it matches the expected
        if selected_vintage_id is not None:
            passed = (selected_vintage_id == expected_vintage_id)
            return ValidationResult(
                passed=passed,
                invariant='PIT-3',
                message=f'Selected {selected_vintage_id} == expected {expected_vintage_id}' if passed
                        else f'Revision leakage: selected {selected_vintage_id}, expected {expected_vintage_id}',
                details={
                    'selected_vintage_id': selected_vintage_id,
                    'expected_vintage_id': expected_vintage_id,
                    'vintage_time': latest_vintage[0].isoformat()
                }
            )
        
        # If no selected_vintage_id provided, just return the expected
        return ValidationResult(
            passed=True,
            invariant='PIT-3',
            message=f'Expected vintage: {expected_vintage_id} at {latest_vintage[0]}',
            details={
                'expected_vintage_id': expected_vintage_id,
                'vintage_time': latest_vintage[0].isoformat()
            }
        )
    
    def check_no_interpolation(self, feature: Dict[str, Any]) -> ValidationResult:
        """PIT-4: NO interpolation (AS-OF JOIN only)."""
        is_interpolated = feature.get('is_interpolated', False)
        
        return ValidationResult(
            passed=not is_interpolated,
            invariant='PIT-4',
            message='No interpolation used' if not is_interpolated 
                    else 'Interpolation detected (AS-OF JOIN violation)',
            details={'is_interpolated': is_interpolated}
        )
    
    def check_timezone_aware(self, dt: datetime) -> ValidationResult:
        """PIT-5: All timestamps MUST be UTC (not just timezone-aware)."""
        if dt is None:
            return ValidationResult(
                passed=False,
                invariant='PIT-5',
                message='Timestamp is None',
                details={}
            )
        
        # Check that timestamp is UTC (not just any timezone)
        is_utc = dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) == pytz.UTC.utcoffset(dt)
        
        return ValidationResult(
            passed=is_utc,
            invariant='PIT-5',
            message='Timestamp is UTC' if is_utc else f'Timestamp {dt} is not UTC',
            details={'timestamp': dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)}
        )
    
    def check_target_timing(self, prediction_timestamp: datetime,
                            target_start: datetime, target_end: datetime) -> ValidationResult:
        """PIT-6: prediction_timestamp < target_start < target_end."""
        prediction_timestamp = self._ensure_utc(prediction_timestamp)
        target_start = self._ensure_utc(target_start)
        target_end = self._ensure_utc(target_end)
        
        passed = (prediction_timestamp < target_start < target_end)
        
        return ValidationResult(
            passed=passed,
            invariant='PIT-6',
            message=f'{prediction_timestamp} < {target_start} < {target_end}' if passed
                    else f'Temporal ordering violation',
            details={
                'prediction_timestamp': prediction_timestamp.isoformat(),
                'target_start': target_start.isoformat(),
                'target_end': target_end.isoformat()
            }
        )
    
    def check_observation_ordering(self, event_time: datetime, release_time: datetime,
                                   source_available_time: datetime,
                                   system_available_time: datetime) -> ValidationResult:
        """PIT-7: event_time <= release_time <= source_available_time <= system_available_time."""
        event_time = self._ensure_utc(event_time)
        release_time = self._ensure_utc(release_time)
        source_available_time = self._ensure_utc(source_available_time)
        system_available_time = self._ensure_utc(system_available_time)
        
        passed = (event_time <= release_time <= source_available_time <= system_available_time)
        
        return ValidationResult(
            passed=passed,
            invariant='PIT-7',
            message=f'{event_time} <= {release_time} <= {source_available_time} <= {system_available_time}'
                    if passed else 'Temporal ordering violation',
            details={
                'event_time': event_time.isoformat(),
                'release_time': release_time.isoformat(),
                'source_available_time': source_available_time.isoformat(),
                'system_available_time': system_available_time.isoformat()
            }
        )
    
    def validate(self, feature: Dict[str, Any], 
                 prediction_timestamp: datetime) -> PITValidationReport:
        """Run all PIT validations for a feature."""
        results = []
        
        # PIT-1
        results.append(self.check_available_time(feature, prediction_timestamp))
        
        # PIT-4
        results.append(self.check_no_interpolation(feature))
        
        # PIT-5
        if feature.get('available_time'):
            results.append(self.check_timezone_aware(feature['available_time']))
        
        # PIT-3 (if vintages exist)
        if 'vintages' in feature:
            results.append(self.check_vintage_selection(
                feature['vintages'], prediction_timestamp
            ))
        
        # PIT-6 (if target info exists)
        if 'target_start' in feature and 'target_end' in feature:
            results.append(self.check_target_timing(
                prediction_timestamp,
                feature['target_start'],
                feature['target_end']
            ))
        
        # PIT-7 (if observation times exist)
        if all(k in feature for k in ['event_time', 'release_time', 
                                       'source_available_time', 'system_available_time']):
            results.append(self.check_observation_ordering(
                feature['event_time'],
                feature['release_time'],
                feature['source_available_time'],
                feature['system_available_time']
            ))
        
        feature_id = feature.get('feature_id', 'unknown')
        
        return PITValidationReport(
            feature_id=feature_id,
            prediction_timestamp=prediction_timestamp,
            results=results
        )
