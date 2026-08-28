from fastapi import APIRouter, Query
from datetime import datetime
from typing import List

router = APIRouter(prefix="/v1/fx", tags=["interpretation"])

@router.get("/interpretation")
async def get_interpretation(pair: str = Query(..., description="Par de divisas")):
    """
    Interpretación económica para Why Now?
    Versión simplificada con razones económicas estáticas
    """
    # Interpretaciones según el par
    interpretations = {
        "USD/JPY": [
            "La divergencia de política monetaria entre la Fed y el BoJ se mantiene elevada, reforzando el soporte relativo del USD frente al JPY.",
            "El diferencial de rendimientos US-Japón se mantiene en niveles atractivos, confirmando el principal driver macro de la señal.",
            "El régimen de riesgo es cauteloso, lo que limita la exposición a posiciones alcistas en USD/JPY.",
            "El edge económico no alcanza el umbral mínimo requerido, por lo que la señal no es accionable actualmente."
        ],
        "EUR/USD": [
            "El diferencial de crecimiento entre EE.UU. y la Eurozona continúa favoreciendo al USD.",
            "La política monetaria del BCE se mantiene acomodaticia, presionando al EUR.",
            "El entorno de riesgo global sigue siendo incierto, afectando al EUR como moneda de financiamiento.",
            "El edge económico es insuficiente para justificar una posición accionable."
        ],
        "GBP/USD": [
            "La incertidumbre política en el Reino Unido continúa pesando sobre la libra.",
            "El Banco de Inglaterra mantiene una postura cautelosa frente a la Fed.",
            "El diferencial de rendimientos favorece al USD frente al GBP.",
            "La señal no alcanza el umbral mínimo de edge económico."
        ],
        "USD/CHF": [
            "El franco suizo mantiene su estatus de refugio seguro.",
            "El diferencial de tasas entre EE.UU. y Suiza sigue favoreciendo al USD.",
            "La aversión al riesgo global podría fortalecer al CHF.",
            "El edge económico actual no justifica una posición activa."
        ]
    }
    
    # Normalizar par para buscar
    pair_normalized = pair.upper()
    
    # Si no existe interpretación para el par, usar una genérica
    if pair_normalized not in interpretations:
        interpretations[pair_normalized] = [
            f"La señal para {pair} muestra una dirección definida.",
            "El contexto macroeconómico respalda la dirección de la señal.",
            "El régimen de riesgo actual es consistente con la tesis.",
            "El edge económico debe superar el umbral mínimo para ser accionable."
        ]
    
    return {
        "pair": pair,
        "interpretation": interpretations[pair_normalized],
        "timestamp": datetime.now().isoformat()
    }
