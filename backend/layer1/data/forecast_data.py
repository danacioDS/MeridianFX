"""
Datos de forecast para los pares de divisas.
"""

FORECAST_DATA = {
    "USD/JPY": {
        "pair": "USD/JPY",
        "direction": "DOWN",
        "probability": 0.50,
        "spot": {"price": 159.7170, "change_pct": 0.25, "change_abs": 0.3960},
        "forecasts": {
            "30d": {"direction": "DOWN", "expected_return": -0.01, "probability": 0.502, "ci_95_lower": 158.3291, "ci_95_upper": 161.1049},
            "60d": {"direction": "DOWN", "expected_return": -0.02, "probability": 0.502, "ci_95_lower": 156.9411, "ci_95_upper": 162.4929},
            "90d": {"direction": "DOWN", "expected_return": -0.03, "probability": 0.502, "ci_95_lower": 155.5532, "ci_95_upper": 163.8808}
        },
        "volatility": 0.12,
        "regime": "RISK_OFF",
        "economic_filter": {
            "edge_ratio": 0.0,
            "actionable": False,
            "minimum_edge": 1.5,
            "gross_return": 0.0,
            "net_return": -0.05
        }
    },
    "USD/BOB": {
        "pair": "USD/BOB",
        "direction": "DOWN",
        "probability": 0.63,
        "spot": {"price": 11.84, "change_pct": 3.83, "change_abs": 0.4367},
        "forecasts": {
            "30d": {"direction": "UP", "expected_return": 1.89, "probability": 0.878, "ci_95_lower": 11.60, "ci_95_upper": 12.08},
            "60d": {"direction": "UP", "expected_return": 3.78, "probability": 0.878, "ci_95_lower": 11.36, "ci_95_upper": 12.32},
            "90d": {"direction": "UP", "expected_return": 5.67, "probability": 0.878, "ci_95_lower": 11.13, "ci_95_upper": 12.55}
        },
        "volatility": 0.18,
        "regime": "RISK_OFF",
        "economic_filter": {
            "edge_ratio": 0.76,
            "actionable": False,
            "minimum_edge": 1.5,
            "gross_return": -0.23,
            "net_return": -0.28
        }
    },
    "EUR/USD": {
        "pair": "EUR/USD",
        "direction": "UP",
        "probability": 0.53,
        "spot": {"price": 1.1050, "change_pct": 0.32, "change_abs": 0.0035},
        "forecasts": {
            "30d": {"direction": "UP", "expected_return": 0.45, "probability": 0.53, "ci_95_lower": 1.0950, "ci_95_upper": 1.1150},
            "60d": {"direction": "UP", "expected_return": 0.90, "probability": 0.53, "ci_95_lower": 1.0850, "ci_95_upper": 1.1250},
            "90d": {"direction": "UP", "expected_return": 1.35, "probability": 0.53, "ci_95_lower": 1.0750, "ci_95_upper": 1.1350}
        },
        "volatility": 0.08,
        "regime": "RISK_ON",
        "economic_filter": {
            "edge_ratio": 0.33,
            "actionable": False,
            "minimum_edge": 1.5,
            "gross_return": 0.10,
            "net_return": 0.05
        }
    },
    "GBP/USD": {
        "pair": "GBP/USD",
        "direction": "DOWN",
        "probability": 0.70,
        "spot": {"price": 1.2850, "change_pct": -0.15, "change_abs": -0.0019},
        "forecasts": {
            "30d": {"direction": "DOWN", "expected_return": -0.28, "probability": 0.70, "ci_95_lower": 1.2750, "ci_95_upper": 1.2950},
            "60d": {"direction": "DOWN", "expected_return": -0.56, "probability": 0.70, "ci_95_lower": 1.2650, "ci_95_upper": 1.3050},
            "90d": {"direction": "DOWN", "expected_return": -0.84, "probability": 0.70, "ci_95_lower": 1.2550, "ci_95_upper": 1.3150}
        },
        "volatility": 0.10,
        "regime": "RISK_OFF",
        "economic_filter": {
            "edge_ratio": 0.93,
            "actionable": False,
            "minimum_edge": 1.5,
            "gross_return": -0.28,
            "net_return": -0.33
        }
    }
}
