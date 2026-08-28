"""
FRED Data Source — Datos macroeconómicos de la Reserva Federal.
"""

import os
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FredSeries:
    """Definición de una serie FRED."""
    id: str
    name: str
    description: str
    frequency: str  # d, m, q, a
    unit: str
    fx_relevance: str  # HIGH, MEDIUM, LOW


# Series macro relevantes para FX
MACRO_SERIES = {
    # Política monetaria
    "FEDFUNDS": FredSeries(
        id="FEDFUNDS",
        name="Fed Funds Rate",
        description="Effective Federal Funds Rate",
        frequency="d",
        unit="%",
        fx_relevance="HIGH"
    ),
    "DFF": FredSeries(
        id="DFF",
        name="Fed Funds Rate (Daily)",
        description="Daily Federal Funds Rate",
        frequency="d",
        unit="%",
        fx_relevance="HIGH"
    ),
    
    # Inflación
    "CPIAUCSL": FredSeries(
        id="CPIAUCSL",
        name="CPI All Urban Consumers",
        description="Consumer Price Index for All Urban Consumers",
        frequency="m",
        unit="index",
        fx_relevance="HIGH"
    ),
    "CORESTICKM159SFRBATL": FredSeries(
        id="CORESTICKM159SFRBATL",
        name="Core CPI (Sticky)",
        description="Sticky Price CPI",
        frequency="m",
        unit="%",
        fx_relevance="HIGH"
    ),
    
    # Mercado laboral
    "UNRATE": FredSeries(
        id="UNRATE",
        name="Unemployment Rate",
        description="Civilian Unemployment Rate",
        frequency="m",
        unit="%",
        fx_relevance="MEDIUM"
    ),
    "PAYEMS": FredSeries(
        id="PAYEMS",
        name="Nonfarm Payrolls",
        description="Total Nonfarm Payrolls",
        frequency="m",
        unit="thousands",
        fx_relevance="MEDIUM"
    ),
    
    # Crecimiento
    "GDPC1": FredSeries(
        id="GDPC1",
        name="Real GDP",
        description="Real Gross Domestic Product",
        frequency="q",
        unit="billions USD",
        fx_relevance="HIGH"
    ),
    "GDP": FredSeries(
        id="GDP",
        name="Nominal GDP",
        description="Gross Domestic Product",
        frequency="q",
        unit="billions USD",
        fx_relevance="MEDIUM"
    ),
    
    # Tasas de interés
    "DGS10": FredSeries(
        id="DGS10",
        name="10-Year Treasury Yield",
        description="10-Year Treasury Constant Maturity Rate",
        frequency="d",
        unit="%",
        fx_relevance="HIGH"
    ),
    "DGS2": FredSeries(
        id="DGS2",
        name="2-Year Treasury Yield",
        description="2-Year Treasury Constant Maturity Rate",
        frequency="d",
        unit="%",
        fx_relevance="HIGH"
    ),
    "T10Y2Y": FredSeries(
        id="T10Y2Y",
        name="10Y-2Y Yield Spread",
        description="10-Year Treasury minus 2-Year Treasury",
        frequency="d",
        unit="%",
        fx_relevance="HIGH"
    ),
    
    # Confianza
    "UMCSENT": FredSeries(
        id="UMCSENT",
        name="Consumer Sentiment",
        description="University of Michigan Consumer Sentiment",
        frequency="m",
        unit="index",
        fx_relevance="MEDIUM"
    ),
    "CSCICP03USM665S": FredSeries(
        id="CSCICP03USM665S",
        name="Consumer Confidence",
        description="Consumer Confidence Indicator",
        frequency="m",
        unit="index",
        fx_relevance="MEDIUM"
    ),
}


class FredDataSource:
    """
    Fuente de datos macro FRED.
    
    Obtiene series de la API de FRED y las transforma
    para su uso en el Decision Context.
    """
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            logger.warning("FRED_API_KEY not set. Using simulated data.")
        self._cache = {}
        self._last_fetch = {}
    
    def get_series(self, series_id: str) -> Optional[FredSeries]:
        """Obtiene la definición de una serie."""
        return MACRO_SERIES.get(series_id.upper())
    
    def get_all_series(self) -> Dict[str, FredSeries]:
        """Obtiene todas las series disponibles."""
        return MACRO_SERIES
    
    async def fetch_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene una serie de FRED.
        
        Args:
            series_id: ID de la serie FRED
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            limit: Número de observaciones
            
        Returns:
            Diccionario con los datos de la serie
        """
        if not self.api_key:
            return self._simulate_series(series_id)
        
        # Verificar caché
        cache_key = f"{series_id}_{start_date}_{end_date}_{limit}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {series_id}")
            return self._cache[cache_key]
        
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": limit,
                "sort_order": "desc"
            }
            
            if start_date:
                params["observation_start"] = start_date
            if end_date:
                params["observation_end"] = end_date
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/series/observations",
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"FRED API error: {response.status_code}")
                    return self._simulate_series(series_id)
                
                data = response.json()
                
                # Parsear observaciones
                observations = []
                for obs in data.get("observations", []):
                    if obs.get("value") != ".":
                        observations.append({
                            "date": obs.get("date"),
                            "value": float(obs.get("value", 0))
                        })
                
                result = {
                    "series_id": series_id,
                    "observations": observations,
                    "last_updated": datetime.now().isoformat(),
                    "source": "FRED"
                }
                
                # Guardar en caché
                self._cache[cache_key] = result
                self._last_fetch[series_id] = datetime.now()
                
                return result
                
        except Exception as e:
            logger.error(f"Error fetching {series_id}: {e}")
            return self._simulate_series(series_id)
    
    def _simulate_series(self, series_id: str) -> Dict[str, Any]:
        """Genera datos simulados para una serie (fallback)."""
        series = self.get_series(series_id)
        
        # Datos simulados según tipo de serie
        values = {
            "FEDFUNDS": [5.25, 5.25, 5.00, 5.00, 4.75],
            "CPIAUCSL": [310.0, 312.0, 313.5, 315.0, 316.2],
            "UNRATE": [3.8, 3.7, 3.8, 3.9, 3.8],
            "GDPC1": [22000, 22150, 22300, 22450, 22600],
            "DGS10": [4.2, 4.3, 4.1, 4.2, 4.4],
            "DGS2": [4.8, 4.7, 4.6, 4.7, 4.9],
            "T10Y2Y": [-0.6, -0.4, -0.5, -0.5, -0.5],
            "CORESTICKM159SFRBATL": [4.5, 4.4, 4.3, 4.2, 4.1],
            "PAYEMS": [156000, 156500, 157000, 157500, 158000],
            "UMCSENT": [67.0, 68.5, 69.0, 68.0, 67.5],
            "CSCICP03USM665S": [98.5, 99.0, 98.5, 98.0, 97.5],
        }
        
        default_values = [100, 101, 102, 101, 100]
        series_values = values.get(series_id.upper(), default_values)
        
        # Generar fechas
        end_date = datetime.now()
        dates = []
        for i in range(len(series_values)):
            dates.append((end_date - timedelta(days=i*30)).strftime("%Y-%m-%d"))
        
        observations = [
            {"date": dates[i], "value": val}
            for i, val in enumerate(reversed(series_values))
        ]
        
        return {
            "series_id": series_id,
            "observations": observations,
            "last_updated": datetime.now().isoformat(),
            "source": "SIMULATED",
            "warning": "FRED_API_KEY not set"
        }
    
    async def get_macro_context(self) -> Dict[str, Any]:
        """
        Obtiene el contexto macro completo para el Decision Context.
        
        Returns:
            Diccionario con todas las series macro actualizadas.
        """
        macro_context = {
            "timestamp": datetime.now().isoformat(),
            "source": "FRED",
            "series": {},
            "summary": {}
        }
        
        # Obtener todas las series relevantes
        for series_id in MACRO_SERIES:
            data = await self.fetch_series(series_id, limit=5)
            if data and data.get("observations"):
                latest = data["observations"][0]
                previous = data["observations"][1] if len(data["observations"]) > 1 else None
                
                macro_context["series"][series_id] = {
                    "series": MACRO_SERIES[series_id],
                    "latest": latest,
                    "previous": previous,
                    "all_observations": data["observations"],
                    "source": data.get("source", "FRED"),
                    "warning": data.get("warning")
                }
        
        # Generar resumen
        macro_context["summary"] = self._generate_summary(macro_context["series"])
        
        return macro_context
    
    def _generate_summary(self, series_data: Dict) -> Dict[str, Any]:
        """Genera un resumen del contexto macro."""
        summary = {
            "fed_funds": None,
            "inflation": None,
            "unemployment": None,
            "gdp_growth": None,
            "yield_10y": None,
            "yield_2y": None,
            "yield_spread": None,
            "consumer_sentiment": None
        }
        
        for series_id, data in series_data.items():
            if not data.get("latest"):
                continue
            
            latest_value = data["latest"]["value"]
            
            if series_id in ["FEDFUNDS", "DFF"]:
                summary["fed_funds"] = latest_value
            
            elif series_id in ["CPIAUCSL", "CORESTICKM159SFRBATL"]:
                summary["inflation"] = latest_value
            
            elif series_id == "UNRATE":
                summary["unemployment"] = latest_value
            
            elif series_id == "GDPC1":
                # Calcular crecimiento anualizado aproximado
                if len(data.get("all_observations", [])) >= 4:
                    current = data["all_observations"][0]["value"]
                    previous = data["all_observations"][3]["value"]
                    growth = ((current - previous) / previous) * 100
                    summary["gdp_growth"] = round(growth, 2)
            
            elif series_id == "DGS10":
                summary["yield_10y"] = latest_value
            
            elif series_id == "DGS2":
                summary["yield_2y"] = latest_value
            
            elif series_id == "T10Y2Y":
                summary["yield_spread"] = latest_value
            
            elif series_id in ["UMCSENT", "CSCICP03USM665S"]:
                summary["consumer_sentiment"] = latest_value
        
        return summary
