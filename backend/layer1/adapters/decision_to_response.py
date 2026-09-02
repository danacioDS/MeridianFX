from datetime import datetime
from typing import Optional
from ..models.responses import (
    ForecastResponse, Prediction, Decision, Lineage,
    DriversResponse, ShapContribution, MacroRegime, Rag, RagSignal,
    RankingResponse, RankedOpportunity,
    PerformanceResponse, StatisticalMetrics, EconomicMetrics, DegradationMetrics
)

class DecisionAdapter:
    @staticmethod
    def to_forecast_response(decision_data: dict, pair: str) -> ForecastResponse:
        return ForecastResponse(
            pair=pair,
            timestamp=datetime.now(),
            prediction=Prediction(
                direction=decision_data.get('direction', 'UP'),
                probability=decision_data.get('probability', 0.0),
                expected_return=decision_data.get('expected_return'),
                expected_volatility=decision_data.get('expected_volatility'),
                prediction_interval=decision_data.get('prediction_interval')
            ),
            decision=Decision(
                actionable=decision_data.get('actionable', False),
                direction=decision_data.get('direction', 'UP'),
                confidence=decision_data.get('confidence', 0.0),
                signal_strength=decision_data.get('signal_strength'),
                edge_ratio=decision_data.get('edge_ratio'),
                net_return=decision_data.get('net_return'),
                position_size=decision_data.get('position_size')
            ),
            lineage=Lineage(model=decision_data.get('model', {}))
        )

    @staticmethod
    def to_drivers_response(drivers_data: dict, pair: str) -> DriversResponse:
        shap = [
            ShapContribution(
                rank=i+1,
                feature=f['feature'],
                contribution=f['contribution']
            )
            for i, f in enumerate(drivers_data.get('shap', []))
        ]
        
        return DriversResponse(
            pair=pair,
            timestamp=datetime.now(),
            shap=shap,
            macro_regime=MacroRegime(
                risk=drivers_data.get('macro_regime', {}).get('risk'),
                growth=drivers_data.get('macro_regime', {}).get('growth'),
                policy=drivers_data.get('macro_regime', {}).get('policy'),
                inflation=drivers_data.get('macro_regime', {}).get('inflation')
            ),
            rag=Rag(
                fed=RagSignal(
                    sentiment=drivers_data.get('rag', {}).get('fed', {}).get('sentiment'),
                    expectation_gap=drivers_data.get('rag', {}).get('fed', {}).get('expectation_gap')
                ),
                boj=RagSignal(
                    sentiment=drivers_data.get('rag', {}).get('boj', {}).get('sentiment'),
                    expectation_gap=drivers_data.get('rag', {}).get('boj', {}).get('expectation_gap')
                )
            ),
            narrative=drivers_data.get('narrative', ''),
            risks=drivers_data.get('risks', []),
            event_sensitivity=drivers_data.get('event_sensitivity', [])
        )

    @staticmethod
    def to_ranking_response(ranking_data: dict) -> RankingResponse:
        opportunities = [
            RankedOpportunity(
                rank=opp['rank'],
                pair=opp['pair'],
                direction=opp['direction'],
                opportunity_score=opp['opportunity_score'],
                edge_ratio=opp.get('edge_ratio'),
                actionable=opp.get('actionable', False),
                confidence=opp.get('confidence'),
                decision_quality=opp.get('decision_quality'),
                position_size=opp.get('position_size')
            )
            for opp in ranking_data.get('opportunities', [])
        ]
        
        return RankingResponse(
            timestamp=datetime.now(),
            opportunities=opportunities,
            top_opportunity=opportunities[0] if opportunities else None,
            total_actionable=sum(1 for o in opportunities if o.actionable),
            total_pairs=len(opportunities)
        )

    @staticmethod
    def to_performance_response(performance_data: dict, pair: str) -> PerformanceResponse:
        return PerformanceResponse(
            pair=pair,
            timestamp=datetime.now(),
            statistical=StatisticalMetrics(
                directional_accuracy=performance_data.get('directional_accuracy', 0.0),
                auc=performance_data.get('auc', 0.0),
                brier_score=performance_data.get('brier_score', 0.0),
                ece=performance_data.get('ece', 0.0),
                log_loss=performance_data.get('log_loss', 0.0)
            ),
            economic=EconomicMetrics(
                sharpe_ratio=performance_data.get('sharpe_ratio', 0.0),
                sharpe_net=performance_data.get('sharpe_net', 0.0),
                max_drawdown=performance_data.get('max_drawdown', 0.0),
                profit_factor=performance_data.get('profit_factor', 0.0),
                win_rate=performance_data.get('win_rate', 0.0),
                total_return=performance_data.get('total_return', 0.0)
            ),
            regime_performance=performance_data.get('regime_performance', []),
            degradation=DegradationMetrics(
                current_sharpe=performance_data.get('current_sharpe', 0.0),
                historical_sharpe=performance_data.get('historical_sharpe', 0.0),
                drift_detected=performance_data.get('drift_detected', False),
                drift_severity=performance_data.get('drift_severity', 'none')
            )
        )
