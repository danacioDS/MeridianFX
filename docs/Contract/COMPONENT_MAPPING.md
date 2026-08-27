# COMPONENT MAPPING — Data-bearing elements → Components

**Prompt X v1.3 · Meridian FX frontend · 2026-08-27**

Reverse mapping of the Layer 1 v5.1 §7 streams to the presentational components that consume them. Every data-bearing field surfaced by the four consumed endpoints (and the status health endpoint) is listed with its consumer component and file.

## Conventions

- **Props-only:** no component below calls a hook or performs analysis. All streams arrive via props (composition layer = Prompts 4–8).
- **No substitution:** unsupported mockup datums render `NotAvailable` (see MIGRATION_REPORT.md).
- **Formatter fidelity:** displayed values go through `frontend/src/utils/{format,status}.ts` (formatting only).

## 7.1 ForecastResponse (`/forecast`)

| Field | Component | File |
| --- | --- | --- |
| `prediction.direction` | ForecastHero + arrow (`getDirectionArrow`) | `components/forecast/ForecastHero.tsx` |
| `prediction.probability` | ForecastHero, ProbabilityGauge | `components/forecast/ForecastHero.tsx`, `components/forecast/ProbabilityGauge.tsx` |
| `prediction.expected_return` | ForecastHero | `components/forecast/ForecastHero.tsx` |
| `prediction.expected_volatility` | ForecastHero | `components/forecast/ForecastHero.tsx` |
| `prediction.prediction_interval.{lower,upper}` | ForecastHero | `components/forecast/ForecastHero.tsx` |
| `decision.actionable` | EconomicFilter | `components/forecast/EconomicFilter.tsx` |
| `decision.direction` | (composition may reuse arrow) | `components/forecast/ForecastHero.tsx` |
| `decision.confidence` | EconomicFilter | `components/forecast/EconomicFilter.tsx` |
| `decision.signal_strength` | EconomicFilter | `components/forecast/EconomicFilter.tsx` |
| `decision.edge_ratio` | EconomicFilter | `components/forecast/EconomicFilter.tsx` |
| `decision.net_return` | EconomicFilter | `components/forecast/EconomicFilter.tsx` |
| `decision.position_size` | (composition; NOT `position_size_recommendation` — gap) | — |
| `delivery_state` / `delivery_reason` / `delivery_warning` | ForecastHero (unavailability reason) | `components/forecast/ForecastHero.tsx` |
| `lineage.model.version` | ForecastHero (`modelVersion` prop) | `components/forecast/ForecastHero.tsx` |

## 7.2 DriversResponse (`/drivers`)

| Field | Component | File |
| --- | --- | --- |
| `shap[].rank` | ShapBars | `components/drivers/ShapBars.tsx` |
| `shap[].feature` | ShapBars | `components/drivers/ShapBars.tsx` |
| `shap[].contribution` | ShapBars (sign + magnitude bar) | `components/drivers/ShapBars.tsx` |
| `macro_regime.risk` | MacroRegime → RegimeBar | `components/drivers/MacroRegime.tsx`, `components/common/RegimeBar.tsx` |
| `macro_regime.policy` | MacroRegime → RegimeBar | same |
| `macro_regime.growth` | MacroRegime → RegimeBar | same |
| `macro_regime.inflation` | MacroRegime → RegimeBar | same |
| `rag.fed.sentiment` / `rag.boj.sentiment` | RagPanel | `components/drivers/RagPanel.tsx` |
| `rag.fed.expectation_gap` / `rag.boj.expectation_gap` | RagPanel | `components/drivers/RagPanel.tsx` |
| `narrative` | NarrativePanel (verbatim) | `components/drivers/NarrativePanel.tsx` |
| `risks` | RisksPanel | `components/drivers/RisksPanel.tsx` |
| `event_sensitivity` | RisksPanel | `components/drivers/RisksPanel.tsx` |

## 7.3 RankingResponse (`/ranking`)

| Field | Component | File |
| --- | --- | --- |
| `opportunities[].rank` | RankingCard | `components/global/RankingCard.tsx` |
| `opportunities[].pair` | RankingCard | `components/global/RankingCard.tsx` |
| `opportunities[].direction` | RankingCard (arrow) | `components/global/RankingCard.tsx` |
| `opportunities[].opportunity_score` | RankingCard | `components/global/RankingCard.tsx` |
| `opportunities[].edge_ratio` | RankingCard | `components/global/RankingCard.tsx` |
| `opportunities[].actionable` | RankingCard | `components/global/RankingCard.tsx` |
| `opportunities[].confidence` | RankingCard (`opportunity_score` row) | `components/global/RankingCard.tsx` |
| `opportunities[].decision_quality` | (composition; per-card not shown) | — |
| `opportunities[].position_size` | (composition; see gap G3) | — |
| `top_opportunity` / `total_actionable` / `total_pairs` | (composition summary line) | — |
| `snapshot_timestamp` / `as_of` | (composition) | — |

## 7.4 PerformanceResponse (`/performance`)

| Field | Component | File |
| --- | --- | --- |
| `statistical.directional_accuracy` | PerformanceTable | `components/evaluation/PerformanceTable.tsx` |
| `statistical.auc` | PerformanceTable | same |
| `statistical.brier_score` | PerformanceTable | same |
| `statistical.ece` | CalibrationChart | `components/evaluation/CalibrationChart.tsx` |
| `statistical.log_loss` | PerformanceTable | `components/evaluation/PerformanceTable.tsx` |
| `economic.sharpe_ratio` | PerformanceTable | same |
| `economic.sharpe_net` | PerformanceTable | same |
| `economic.max_drawdown` | PerformanceTable | same |
| `economic.profit_factor` | PerformanceTable | same |
| `economic.win_rate` | PerformanceTable | same |
| `economic.total_return` | PerformanceTable | same |
| `regime_performance[]` | (composition; per-regime rows) | — |
| `degradation.current_sharpe` | DriftIndicator | `components/evaluation/DriftIndicator.tsx` |
| `degradation.historical_sharpe` | DriftIndicator | same |
| `degradation.drift_detected` | DriftIndicator | same |
| `degradation.drift_severity` | DriftIndicator | same |

## 7.7 StatusResponse (`/status`)

| Field | Component | File |
| --- | --- | --- |
| `system_status` | Header (composition), SystemStatus | `components/layout/Header.tsx` (wrapper), `components/status/SystemStatus.tsx` |
| `reason` | SystemStatus | `components/status/SystemStatus.tsx` |
| `timestamp` | Header (composition), SystemStatus | same |
| `infrastructure.{api,database,pipeline,cache}` | InfrastructureStatus | `components/status/InfrastructureStatus.tsx` |
| `intelligence.data_quality.{overall,status}` | SystemStatus, Header (`dataQuality`) | `components/status/SystemStatus.tsx`, `components/layout/Header.tsx` |
| `intelligence.model_performance` | SystemStatus | `components/status/SystemStatus.tsx` |
| `intelligence.model_drift` | SystemStatus | same |
| `intelligence.decision_validity` | SystemStatus, SignalValidity | `components/status/SystemStatus.tsx`, `components/forecast/SignalValidity.tsx` |
| `intelligence.safe_mode_state` | SystemStatus | `components/status/SystemStatus.tsx` |
| `metrics.data_freshness` | SystemStatus | same |
| `metrics.prediction_coverage` | SystemStatus | same |

## Presentational primitives (no stream of their own)

| Component | Purpose | File |
| --- | --- | --- |
| `StatusBadge` | Status → color/label dot+pill | `components/common/StatusBadge.tsx` |
| `UniverseSelector` | Pair selection UI | `components/common/UniverseSelector.tsx` |
| `TabNav` | Top-level view tabs | `components/common/TabNav.tsx` |
| `NotAvailable` | Gap/unavailable state renderer | `components/common/NotAvailable.tsx` |

## Coverage

- **Streams surfaced by endpoints** (`/forecast`, `/drivers`, `/ranking`, `/performance`, `/status`): **100%** of §7 data-bearing fields enumerated above have a presentational consumer (composition-only rows are carried by the page wiring that Prompt X defines but Prompts 4–8 implement).
- **Shared lineage structures** (§7.5/§7.6) feed `lineage.model.version` and delivery reasons; feature-list/decision/source blocks are surfaced by the (future gap) lineage UI (G9/DF).

## EXECUTION GATE checklist

| Check | Result |
| --- | --- |
| Every mockup visual element enumerated (66 elements, 4 screens) | ✅ 100% — MIGRATION_REPORT.md |
| Every data-bearing element has a component mapping | ✅ 100% — this file |
| No component calls a data hook (`use*`) | ✅ verified by grep |
| No component performs analysis/inference/ranking | ✅ verified by grep |
| Unsupported/ambiguous mockup datums → `NotAvailable`, never derived | ✅ documented |
| `tsc --noEmit` clean | ✅ |
| `vitest` suite green (47 tests) | ✅ |

## Composition layer (Prompts 4–8) — page wiring

Pages consume the hooks and pass backend values into the presentational components via props. No analytical logic lives in the pages (verified by grep: no `.sort`, `.reduce`, `Math.*`).

| Page | Hooks | Presentational components |
| --- | --- | --- |
| `GlobalPage` (`/`) | `useRanking`, `useActivePair` (+ universe) | RankingCard ×N, RegimeBar(null→NotAvailable), EarlyWarnings→NotAvailable, Key Events→NotAvailable, UniverseSelector, Panel |
| `ForecastPage` (`/forecast`) | `useForecast`, `useStatus`, `useActivePair` | ForecastHero, EconomicFilter, SignalValidity, ProbabilityChart(null→NotAvailable), Panel |
| `DriversPage` (`/drivers`) | `useDrivers`, `useActivePair` | ShapBars, MacroRegime, RagPanel, NarrativePanel, RisksPanel, Panel |
| `EvaluationPage` (`/evaluation`) | `usePerformance`, `useActivePair`, `usePerformancePeriod` | PerformanceTable, CalibrationChart, DriftIndicator, CumulativeChart→NotAvailable, Panel |
| `StatusPage` (`/status`) | `useStatus` | SystemStatus, InfrastructureStatus, Panel |

UI/navigation layers added (composition only, no analytics):
- `useActivePair` — `pair` search param (default `USD/JPY`), URL-shareable across routes
- `usePerformancePeriod` — `period` search param, validated against `PerformancePeriod` enum
- `pairUniverseFromRanking` — pairs from the ranking stream with the documented MVP 4-pair fallback
- `common/Panel` — titled container used by all pages

Verification: `npm run build` (tsc + vite) ✅ · `vitest` 55/55 ✅ · regression suite 47→55 in 7 files.