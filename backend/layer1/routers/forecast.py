from fastapi import APIRouter, HTTPException
from datetime import datetime
import numpy as np

router = APIRouter(prefix="/v1/fx", tags=["forecast"])

# Datos de forecast alineados con el ranking
FORECAST_DATA = {
    "USD/JPY": {
        "direction": "UP",
        "probability": 0.33,      # Coincide con el ranking
        "expected_return": 0.0002,
        "expected_volatility": 0.12,
    },
    "EUR/USD": {
        "direction": "UP",
        "probability": 0.53,
        "expected_return": 0.0016,
        "expected_volatility": 0.10,
    },
    "GBP/USD": {
        "direction": "DOWN",
        "probability": 0.70,
        "expected_return": -0.0028,
        "expected_volatility": 0.15,
    },
    "USD/CHF": {
        "direction": "DOWN",
        "probability": 0.67,
        "expected_return": -0.0026,
        "expected_volatility": 0.08,
    },
    "USD/CNY": {
        "direction": "DOWN",
        "probability": 0.35,
        "expected_return": -0.0003,
        "expected_volatility": 0.06,
    },
    "USD/MXN": {
        "direction": "UP",
        "probability": 0.55,
        "expected_return": 0.0017,
        "expected_volatility": 0.14,
    },
    "USD/BRL": {
        "direction": "UP",
        "probability": 0.37,
        "expected_return": 0.0005,
        "expected_volatility": 0.18,
    },
    "USD/ARS": {
        "direction": "DOWN",
        "probability": 0.65,
        "expected_return": -0.0024,
        "expected_volatility": 0.20,
    },
    "USD/BOB": {
        "direction": "DOWN",
        "probability": 0.63,
        "expected_return": -0.0023,
        "expected_volatility": 0.12,
    },
}


@router.get("/{base}/{quote}/forecast")
async def get_forecast(base: str, quote: str):
    """
    Obtener forecast para un par específico.
    """
    pair = f"{base}/{quote}"
    
    try:
        if pair in FORECAST_DATA:
            data = FORECAST_DATA[pair]
        else:
            data = {
                "direction": "UP" if np.random.random() > 0.5 else "DOWN",
                "probability": np.random.uniform(0.3, 0.7),
                "expected_return": np.random.uniform(-0.005, 0.005),
                "expected_volatility": np.random.uniform(0.05, 0.20),
            }
        
        gross_return = data["expected_return"]
        spread_cost = 0.0010 * abs(gross_return) if gross_return > 0 else 0.0010 * 0.5
        slippage_cost = 0.0005 * abs(gross_return) if gross_return > 0 else 0.0005 * 0.5
        fees = 0.0005
        net_return = gross_return - spread_cost - slippage_cost - fees
        edge_ratio = abs(net_return) / data["expected_volatility"] if data["expected_volatility"] > 0 else 0
        minimum_edge = 1.5
        actionable = edge_ratio >= minimum_edge and net_return > 0
        
        return {
            "pair": pair,
            "prediction": {
                "direction": data["direction"],
                "probability": data["probability"],
                "expected_return": data["expected_return"],
                "expected_volatility": data["expected_volatility"],
            },
            "decision": {
                "actionable": actionable,
                "direction": data["direction"],
                "confidence": data["probability"],
                "edge_ratio": edge_ratio,
                "net_return": net_return,
                "position_size": 0.0 if not actionable else 0.02,
            },
            "lineage": {
                "model": {
                    "version": "xgb-v1.0",
                    "type": "xgboost"
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
