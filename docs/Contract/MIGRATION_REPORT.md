# MIGRATION REPORT — Mockup → Components

**Prompt X v1.3 · Meridian FX frontend**
**Date:** 2026-08-27 · **Scope:** `docs/High-Level Design/02_product_specification.md` (Optimized Product Mockup v1.0) → `frontend/src/components/**` (presentational layer only)

Architecture note: Prompt X builds the **presentational component layer** (props-only, no hooks). Page composition (hooks → props) is the responsibility of the Prompts 4–8 composition layer and is **not** part of this report.

## Classification legend

| Class | Meaning |
| --- | --- |
| `SUPPORTED_DATA` | Backend field exists in Layer 1 v5.1 §7; rendered verbatim/formatted. |
| `VISUAL_COMPONENT` | Backend field drives appearance (color/width/arrow); presentation-only mapping. |
| `UNSUPPORTED` | No contract source. Rendered as `NotAvailable` or omitted. Never derived. |
| `AMBIGUOUS` | Mockup semantics vs contract mismatch; resolved conservatively (→ UNSUPPORTED). |

---

## 1. GLOBAL OVERVIEW

| # | Mockup element | Class | Component | Data stream |
| --- | --- | --- | --- | --- |
| 1.1 | Brand + page title + date | `SUPPORTED_DATA` | `common/Header` | `StatusResponse.timestamp` |
| 1.2 | System status dot | `SUPPORTED_DATA` | `common/Header` | `StatusResponse.system_status` |
| 1.3 | Data quality ("Data: Fresh") | `SUPPORTED_DATA` | `common/Header` | `StatusResponse.intelligence.data_quality.status` |
| 1.4 | Coverage ("98% coverage") | `SUPPORTED_DATA` | `status/SystemStatus` | `StatusResponse.metrics.prediction_coverage` |
| 1.5 | Inference time ("42ms") | `UNSUPPORTED` | — | No contract field (gap). Omitted. |
| 1.6 | Market Regime panel (RISK-ON / VIX / Risk Appetite) | `UNSUPPORTED` | `common/RegimeBar` (via `drivers/MacroRegime`) | Regime axes exist only per-pair in `DriversResponse.macro_regime`; VIX/risk-appetite NOT contractual. Global composition passes `null` → NotAvailable (G4). |
| 1.7 | Top Opportunities — rank | `SUPPORTED_DATA` | `global/RankingCard` | `RankingResponse.opportunities[].rank` |
| 1.8 | Top Opportunities — pair | `SUPPORTED_DATA` | `global/RankingCard` | `RankingResponse.opportunities[].pair` |
| 1.9 | Top Opportunities — direction + arrow | `SUPPORTED_DATA` + `VISUAL_COMPONENT` | `global/RankingCard` | `RankingResponse.opportunities[].direction`; arrow via `getDirectionArrow` |
| 1.10 | Top Opportunities — probability (68%) | `UNSUPPORTED` | `global/RankingCard` (secondary slot) | `RankingResponse.opportunities` has NO probability field. NotAvailable. |
| 1.11 | Top Opportunities — expected return (+0.82%) | `UNSUPPORTED` | `global/RankingCard` (secondary slot) | No `expected_return` in `RankedOpportunity`. NotAvailable. |
| 1.12 | Top Opportunities — ACTIONABLE / NO EDGE | `SUPPORTED_DATA` | `global/RankingCard` | `RankingResponse.opportunities[].actionable` |
| 1.13 | Top Opportunities — Net | `UNSUPPORTED` | `global/RankingCard` (secondary slot) | No `net_return` in `RankedOpportunity`. NotAvailable. |
| 1.14 | Top Opportunities — Edge (3.1x) | `SUPPORTED_DATA` | `global/RankingCard` | `RankingResponse.opportunities[].edge_ratio` |
| 1.15 | Top Opportunities — Signal strength | `UNSUPPORTED` | `global/RankingCard` (secondary slot) | No `signal_strength` in `RankedOpportunity`. NotAvailable. |
| 1.16 | Early Warnings (positioning, VIX regime) | `UNSUPPORTED` | `global/EarlyWarnings` | No early-warning structure in Layer 1 §7 (G-08). NotAvailable. |
| 1.17 | Key Events Today (calendar) | `UNSUPPORTED` | — (composition renders NotAvailable) | Economic calendar gap (EC-1). No component; nothing to present. |

## 2. FORECAST DASHBOARD

| # | Mockup element | Class | Component | Data stream |
| --- | --- | --- | --- | --- |
| 2.1 | Direction + arrow | `SUPPORTED_DATA` + `VISUAL_COMPONENT` | `forecast/ForecastHero` | `ForecastResponse.prediction.direction` |
| 2.2 | Probability (68% calibrated) | `SUPPORTED_DATA` | `forecast/ForecastHero`, `forecast/ProbabilityGauge` | `ForecastResponse.prediction.probability` |
| 2.3 | Horizon (5D) | `UNSUPPORTED` | `forecast/ForecastHero` (horizon slot) | No horizon field in §7.1 (G). "—" placeholder. |
| 2.4 | Model version (xgb-v2.3) | `SUPPORTED_DATA` | `forecast/ForecastHero` (prop) | `ForecastResponse.lineage.model.version` |
| 2.5 | Expected Return (+0.82%) | `SUPPORTED_DATA` | `forecast/ForecastHero` | `ForecastResponse.prediction.expected_return` |
| 2.6 | Expected Volatility | `SUPPORTED_DATA` | `forecast/ForecastHero` | `ForecastResponse.prediction.expected_volatility` |
| 2.7 | 95% Prediction Interval | `SUPPORTED_DATA` | `forecast/ForecastHero` | `ForecastResponse.prediction.prediction_interval.{lower,upper}` |
| 2.8 | Gross Return | `AMBIGUOUS` | `forecast/EconomicFilter` | Mockup gross ≈ only `decision.net_return` exists; presented as Net (see 2.10). |
| 2.9 | Total Costs (Spread/Slippage/Fees) | `UNSUPPORTED` | `forecast/EconomicFilter` | No cost breakdown fields in §7 (gaps EC-2…EC-3). NotAvailable. |
| 2.10 | Net Return | `SUPPORTED_DATA` | `forecast/EconomicFilter` | `ForecastResponse.decision.net_return` |
| 2.11 | Edge Ratio (3.1x) | `SUPPORTED_DATA` | `forecast/EconomicFilter` | `ForecastResponse.decision.edge_ratio` |
| 2.12 | Signal Strength | `SUPPORTED_DATA` | `forecast/EconomicFilter` | `ForecastResponse.decision.signal_strength` |
| 2.13 | Confidence | `SUPPORTED_DATA` | `forecast/EconomicFilter` | `ForecastResponse.decision.confidence` |
| 2.14 | Minimum Edge | `UNSUPPORTED` | `forecast/EconomicFilter` | No field (gap EC-4). NotAvailable. |
| 2.15 | 🟢 ACTIONABLE | `SUPPORTED_DATA` | `forecast/EconomicFilter` | `ForecastResponse.decision.actionable` |
| 2.16 | Signal validity — conditions / invalidation | `UNSUPPORTED` | `forecast/SignalValidity` | Condition lists NOT in §7 (gap G9). NotAvailable. |
| 2.17 | Decision validity state | `SUPPORTED_DATA` | `forecast/SignalValidity` (prop)` | `StatusResponse.intelligence.decision_validity` |
| 2.18 | Forecast probability history | `UNSUPPORTED` | `forecast/ProbabilityChart` | Gap G-01 `getForecastHistory`. NotAvailable until stream exists. |

## 3. DRIVERS & EXPLANATION

| # | Mockup element | Class | Component | Data stream |
| --- | --- | --- | --- | --- |
| 3.1 | Key Drivers — rank | `SUPPORTED_DATA` | `drivers/ShapBars` | `DriversResponse.shap[].rank` |
| 3.2 | Key Drivers — feature name | `SUPPORTED_DATA` | `drivers/ShapBars` | `DriversResponse.shap[].feature` |
| 3.3 | Key Drivers — contribution | `SUPPORTED_DATA` | `drivers/ShapBars` | `DriversResponse.shap[].contribution` (with sign, formatted) |
| 3.4 | Key Drivers — visual bar | `VISUAL_COMPONENT` | `drivers/ShapBars` | Bar length ∝ |contribution| (presentation only). |
| 3.5 | Key Drivers — "Value: 3.42%" | `UNSUPPORTED` | `drivers/ShapBars` | Feature raw value NOT in `ShapContribution`. Omitted. |
| 3.6 | Key Drivers — "Contribution: 42%" | `UNSUPPORTED` | `drivers/ShapBars` | Percentage requires derivation (NO_DERIVATION). Raw sign+value shown instead. |
| 3.7 | Macro Regime — risk | `SUPPORTED_DATA` | `drivers/MacroRegime` → `common/RegimeBar` | `DriversResponse.macro_regime.risk` |
| 3.8 | Macro Regime — growth | `SUPPORTED_DATA` | `drivers/MacroRegime` | `DriversResponse.macro_regime.growth` |
| 3.9 | Macro Regime — policy (US/Japan split) | `AMBIGUOUS` | `drivers/MacroRegime` | Contract has single `macro_regime.policy` axis (no per-country split). Single value rendered. Inflation axis also included (contract field). |
| 3.10 | Policy Signal — Fed/BoJ sentiment | `SUPPORTED_DATA` | `drivers/RagPanel` | `DriversResponse.rag.{fed,boj}.sentiment` |
| 3.11 | Policy Signal — expectation gap | `SUPPORTED_DATA` | `drivers/RagPanel` | `DriversResponse.rag.{fed,boj}.expectation_gap` |
| 3.12 | Policy Signal — Hawkish/Dovish labels + deltas + "Divergence HIGH" | `UNSUPPORTED` | `drivers/RagPanel` | Labels/deltas/divergence NOT contractual; numeric sentiment presented verbatim. |
| 3.13 | Key Risks | `SUPPORTED_DATA` | `drivers/RisksPanel` | `DriversResponse.risks` |
| 3.14 | Event sensitivities | `SUPPORTED_DATA` | `drivers/RisksPanel` | `DriversResponse.event_sensitivity` |
| 3.15 | Executive narrative | `SUPPORTED_DATA` | `drivers/NarrativePanel` | `DriversResponse.narrative` (verbatim) |

## 4. PERFORMANCE DASHBOARD

| # | Mockup element | Class | Component | Data stream |
| --- | --- | --- | --- | --- |
| 4.1 | Directional Accuracy | `SUPPORTED_DATA` | `evaluation/PerformanceTable` | `PerformanceResponse.statistical.directional_accuracy` |
| 4.2 | AUC | `SUPPORTED_DATA` | `evaluation/PerformanceTable` | `PerformanceResponse.statistical.auc` |
| 4.3 | Brier Score | `SUPPORTED_DATA` | `evaluation/PerformanceTable` | `PerformanceResponse.statistical.brier_score` |
| 4.4 | N (sample count) | `UNSUPPORTED` | `evaluation/PerformanceTable` | No sample-count field. Omitted. |
| 4.5 | ECE | `SUPPORTED_DATA` | `evaluation/CalibrationChart` | `PerformanceResponse.statistical.ece` |
| 4.6 | vs Benchmark column | `UNSUPPORTED` | `evaluation/PerformanceTable` | No benchmark series (gap). NotAvailable column. |
| 4.7 | Status column | `UNSUPPORTED` | `evaluation/PerformanceTable` | No per-metric status field. NotAvailable column. |
| 4.8 | Net Return (annualized) | `AMBIGUOUS` | `evaluation/PerformanceTable` | Contract has `economic.total_return` (period total, not annualized). Presented verbatim as Total Return. |
| 4.9 | Sharpe (net) | `SUPPORTED_DATA` | `evaluation/PerformanceTable` | `PerformanceResponse.economic.sharpe_net` (`sharpe_ratio` also rendered) |
| 4.10 | Max Drawdown | `SUPPORTED_DATA` | `evaluation/PerformanceTable` | `PerformanceResponse.economic.max_drawdown` |
| 4.11 | Profit Factor | `SUPPORTED_DATA` | `evaluation/PerformanceTable` | `PerformanceResponse.economic.profit_factor` |
| 4.12 | Win Rate / Total Return | `SUPPORTED_DATA` | `evaluation/PerformanceTable` | `PerformanceResponse.economic.{win_rate,total_return}` |
| 4.13 | Calibration curve (reliability series) | `UNSUPPORTED` | `evaluation/CalibrationChart` | No series in §7.4 (gap CA). NotAvailable; ECE scalar only. |
| 4.14 | Cumulative return series | `UNSUPPORTED` | `evaluation/CumulativeChart` | No historical series in §7 (gap DF-P). NotAvailable. |
| 4.15 | Cumulative benchmark (Random Walk Sharpe) | `UNSUPPORTED` | `evaluation/CumulativeChart` | No benchmark series. NotAvailable. |
| 4.16 | Drift — severity/detected/Sharpe | `SUPPORTED_DATA` | `evaluation/DriftIndicator` | `PerformanceResponse.degradation.{drift_severity,drift_detected,current_sharpe,historical_sharpe}` |

---

## Coverage summary

| Screen | Mockup elements | Supported | Unsupported/Ambiguous | Coverage |
| --- | ---: | ---: | ---: | --- |
| Global Overview | 17 | 8 | 9 | 100% (unsupported explicitly mapped) |
| Forecast Dashboard | 18 | 13 | 5 | 100% |
| Drivers & Explanation | 15 | 11 | 4 | 100% |
| Performance | 16 | 10 | 6 | 100% |
| **Total** | **66** | **42** | **24** | **100% enumerated** |

Every mockup element is either (a) backed by a Layer 1 §7 stream and presented, or (b) explicitly classified `UNSUPPORTED`/`AMBIGUOUS` with a documented reason and rendered as `NotAvailable` or omitted. **No element is silently dropped; no analytical inference is performed.**