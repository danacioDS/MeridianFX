from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# 7.1 ForecastResponse
class PredictionInterval(BaseModel):
    lower: float
    upper: float

class Prediction(BaseModel):
    direction: str
    probability: float
    expected_return: Optional[float] = None
    expected_volatility: Optional[float] = None
    prediction_interval: Optional[PredictionInterval] = None

class Decision(BaseModel):
    actionable: bool
    direction: str
    confidence: float
    signal_strength: Optional[float] = None
    edge_ratio: Optional[float] = None
    net_return: Optional[float] = None
    position_size: Optional[float] = None

class Lineage(BaseModel):
    model: dict
    source: Optional[str] = None

class ForecastResponse(BaseModel):
    pair: str
    timestamp: datetime
    prediction: Prediction
    decision: Decision
    lineage: Optional[Lineage] = None
    delivery_state: Optional[str] = None
    delivery_reason: Optional[str] = None
    delivery_warning: Optional[str] = None

# 7.2 DriversResponse
class ShapContribution(BaseModel):
    rank: int
    feature: str
    contribution: float

class MacroRegime(BaseModel):
    risk: Optional[str] = None
    growth: Optional[str] = None
    policy: Optional[str] = None
    inflation: Optional[str] = None

class RagSignal(BaseModel):
    sentiment: Optional[float] = None
    expectation_gap: Optional[float] = None

class Rag(BaseModel):
    fed: RagSignal
    boj: RagSignal

class DriversResponse(BaseModel):
    pair: str
    timestamp: datetime
    shap: List[ShapContribution]
    macro_regime: MacroRegime
    rag: Rag
    narrative: str
    risks: List[str]
    event_sensitivity: List[dict]

# 7.3 RankingResponse
class RankedOpportunity(BaseModel):
    rank: int
    pair: str
    direction: str
    opportunity_score: float
    edge_ratio: Optional[float] = None
    actionable: bool
    confidence: Optional[float] = None
    decision_quality: Optional[str] = None
    position_size: Optional[float] = None

class RankingResponse(BaseModel):
    timestamp: datetime
    opportunities: List[RankedOpportunity]
    top_opportunity: Optional[RankedOpportunity] = None
    total_actionable: int
    total_pairs: int
    snapshot_timestamp: Optional[datetime] = None
    as_of: Optional[datetime] = None

# 7.4 PerformanceResponse
class StatisticalMetrics(BaseModel):
    directional_accuracy: float
    auc: float
    brier_score: float
    ece: float
    log_loss: float

class EconomicMetrics(BaseModel):
    sharpe_ratio: float
    sharpe_net: float
    max_drawdown: float
    profit_factor: float
    win_rate: float
    total_return: float

class RegimePerformance(BaseModel):
    regime: str
    return_value: float
    count: int

class DegradationMetrics(BaseModel):
    current_sharpe: float
    historical_sharpe: float
    drift_detected: bool
    drift_severity: str

class PerformanceResponse(BaseModel):
    pair: str
    timestamp: datetime
    statistical: StatisticalMetrics
    economic: EconomicMetrics
    regime_performance: List[RegimePerformance]
    degradation: DegradationMetrics

# 7.7 StatusResponse
class InfrastructureStatus(BaseModel):
    api: str
    database: str
    pipeline: str
    cache: str

class IntelligenceStatus(BaseModel):
    data_quality: dict
    model_performance: dict
    model_drift: dict
    decision_validity: dict
    safe_mode_state: str

class MetricsStatus(BaseModel):
    data_freshness: str
    prediction_coverage: float

class StatusResponse(BaseModel):
    system_status: str
    reason: Optional[str] = None
    timestamp: datetime
    infrastructure: InfrastructureStatus
    intelligence: IntelligenceStatus
    metrics: MetricsStatus
