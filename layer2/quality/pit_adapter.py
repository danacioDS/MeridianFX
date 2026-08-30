"""
PIT Adapter — Layer 2 ↔ Layer 4

Layer 4 owns PIT validation.
Layer 2 consumes the validation result before prediction.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from layer4.quality.pit_validator import PITValidator


class PITAdapter:
    """
    Adapter between Layer 2 DecisionEngine and Layer 4 PITValidator.

    The adapter does not implement PIT rules itself.
    Layer 4 remains the authoritative PIT validation layer.
    """

    def __init__(self):
        self.validator = PITValidator()

    def validate_prediction_inputs(
        self,
        feature: Dict[str, Any],
        prediction_timestamp: datetime,
    ) -> Dict[str, Any]:
        """
        Validate prediction inputs using Layer 4.

        Returns a serializable result suitable for Layer 2/API consumers.
        """

        report = self.validator.validate(
            feature,
            prediction_timestamp,
        )

        return {
            "passed": report.passed,
            "feature_id": report.feature_id,
            "prediction_timestamp": report.prediction_timestamp.isoformat(),
            "failures": [
                {
                    "invariant": failure.invariant,
                    "message": failure.message,
                    "details": failure.details,
                }
                for failure in report.failures
            ],
            "results": [
                {
                    "invariant": result.invariant,
                    "passed": result.passed,
                    "message": result.message,
                    "details": result.details,
                }
                for result in report.results
            ],
        }
