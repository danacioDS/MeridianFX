"""
Price Router — cotización actual, histórico y predicción.
"""

from datetime import datetime

from fastapi import APIRouter, Path, Query

from layer2.data.provider import DataProvider
from layer2.features.technical import TechnicalFeatures
from layer2.engine import DecisionEngine


router = APIRouter(prefix="/v1/fx", tags=["price"])

data_provider = DataProvider()
engine = DecisionEngine()


CURRENCY_NAMES = {
    "USD/JPY": {
        "base": "USD",
        "quote": "JPY",
        "base_name": "Dólar",
        "quote_name": "Yen",
    },
    "EUR/USD": {
        "base": "EUR",
        "quote": "USD",
        "base_name": "Euro",
        "quote_name": "Dólar",
    },
    "GBP/USD": {
        "base": "GBP",
        "quote": "USD",
        "base_name": "Libra",
        "quote_name": "Dólar",
    },
    "USD/CHF": {
        "base": "USD",
        "quote": "CHF",
        "base_name": "Dólar",
        "quote_name": "Franco",
    },
    "USD/CNY": {
        "base": "USD",
        "quote": "CNY",
        "base_name": "Dólar",
        "quote_name": "Yuan",
    },
    "USD/MXN": {
        "base": "USD",
        "quote": "MXN",
        "base_name": "Dólar",
        "quote_name": "Peso",
    },
    "USD/BRL": {
        "base": "USD",
        "quote": "BRL",
        "base_name": "Dólar",
        "quote_name": "Real",
    },
    "USD/ARS": {
        "base": "USD",
        "quote": "ARS",
        "base_name": "Dólar",
        "quote_name": "Peso",
    },
    "USD/BOB": {
        "base": "USD",
        "quote": "BOB",
        "base_name": "Dólar",
        "quote_name": "Boliviano",
    },
}


@router.get("/{pair:path}/price")
async def get_price(
    pair: str = Path(..., description="Currency pair, e.g. USD/BOB"),
    period: str = Query(
        "1y",
        description="Historical period: 1m, 3m, 6m, 1y",
    ),
):
    """Obtiene cotización, histórico y señal del modelo."""

    pair = pair.upper()

    result = data_provider.get_historical(
        pair,
        period=period,
        interval="1d",
    )

    df = result["data"]

    if df.empty:
        return {
            "error": "No data available",
            "pair": pair,
        }

    # DataProvider canonical contract:
    # Open / High / Low / Close / Volume

    current_price = float(df["Close"].iloc[-1])

    previous_price = (
        float(df["Close"].iloc[-2])
        if len(df) > 1
        else current_price
    )

    change_abs = current_price - previous_price

    change_percent = (
        (change_abs / previous_price) * 100
        if previous_price != 0
        else 0.0
    )

    history = []

    for idx, row in df.iterrows():
        history.append(
            {
                "date": idx.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]),
            }
        )

    # ---------------------------------------------------------
    # XGBoost prediction
    # ---------------------------------------------------------

    direction = "UNKNOWN"
    probability = 0.5

    try:
        df_features = TechnicalFeatures.generate(df)

        feature_cols = TechnicalFeatures.get_feature_names()

        latest_features = (
            df_features[feature_cols]
            .iloc[-1:]
            .dropna()
        )

        if (
            not latest_features.empty
            and engine.xgb_model
            and engine.xgb_model.model
        ):
            prediction = engine.xgb_model.predict(
                latest_features
            )

            direction = prediction.get(
                "direction",
                "UNKNOWN",
            )

            probability = float(
                prediction.get(
                    "probability",
                    0.5,
                )
            )

    except Exception as exc:
        print(
            f"⚠️ Price prediction unavailable: "
            f"{type(exc).__name__}: {exc}"
        )

    info = CURRENCY_NAMES.get(pair, {})

    return {
        "pair": pair,
        "base": info.get(
            "base",
            pair.split("/")[0],
        ),
        "quote": info.get(
            "quote",
            pair.split("/")[1],
        ),
        "base_name": info.get(
            "base_name",
            pair.split("/")[0],
        ),
        "quote_name": info.get(
            "quote_name",
            pair.split("/")[1],
        ),
        "current_price": current_price,
        "previous_price": previous_price,
        "change_abs": round(change_abs, 6),
        "change_percent": round(
            change_percent,
            4,
        ),
        "direction": direction,
        "probability": round(
            probability,
            4,
        ),
        "period": period,
        "source": result.get(
            "provider",
            "unknown",
        ),
        "freshness": result.get(
            "freshness",
            "UNKNOWN",
        ),
        "last_date": (
            result["last_date"].strftime("%Y-%m-%d")
            if result.get("last_date")
            else None
        ),
        "timestamp": datetime.now().isoformat(),
        "history": history[-100:],
        "info": (
            f"1 {info.get('base_name', 'USD')} = "
            f"{current_price:.4f} "
            f"{info.get('quote_name', pair.split('/')[1])}"
        ),
    }
