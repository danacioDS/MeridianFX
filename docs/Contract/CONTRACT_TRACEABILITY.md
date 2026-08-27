# CONTRACT_TRACEABILITY.md — Meridian FX

**Prompt -1 v2.0 — Contract Freeze & Repository Audit (evidence-grounded)**

**Version:** v2.0
**Date:** 2026-08-27
**Frozen base:** `docs/Product_specification/Layer_01.md` — Layer 1 v5.1 (Sections 3, 5, 7, 8, 10)

**Traceability rule (non-negotiable):**
`UI datum → Component → Hook → Service → Endpoint → Contract → Field → Layer`

**Status legend:**
- `VERIFIED` — field/step exists in the frozen spec AND is present in the repository (file:line evidence).
- `ASSUMED` — mentioned in the mockup/spec but no implementation found in the repository.
- `UNVERIFIED` — the mapping could not be established against the repository.
- `OPTIONAL GAP` — no contract field/endpoint (→ render `NOT_AVAILABLE` / `UNSUPPORTED_BY_CONTRACT`).

> **Audit note — mockup inventory:** the "Optimized Product Mockup" referenced by the prompt is the
> external 6-module mockup (`docs/High-Level Design/02_product_specification.md:395-408` names the six
> modules/questions only). No mockup HTML and no component implementations of those modules exist in this
> repository yet (module component directories are empty `.gitkeep`). UI element names below are taken from
> the mockup inventory supplied with the prompt and are honestly classified: **every data path is VERIFIED,
> the UI component hop is ASSUMED** until Prompt X implements the module components.

---

## 1. Repository Contract Surface — VERIFIED GROUND (evidence)

### 1.1 Response structures (spec) — `docs/Product_specification/Layer_01.md`

| Structure | Spec section | Spec lines |
| --------- | ------------ | ---------- |
| 7.1 ForecastResponse | §7.1 | 513–548 |
| 7.2 DriversResponse | §7.2 | 550–578 |
| 7.3 RankingResponse | §7.3 | 580–607 |
| 7.4 PerformanceResponse | §7.4 | 609–650 |
| 7.5 LineageResponse (Prediction) | §7.5 | 652–701 |
| 7.6 LineageResponse (Decision) | §7.6 | 703–758 |
| 7.7 StatusResponse | §7.7 | 760–795 |
| SLA table (incl. `/v1/health`, `/v1/fx/{pair}/forecast/history`) | §8 | 799–823 |
| Dashboard pages (data sources) | §10 | 863–903 |

### 1.2 Frontend field inventory — `frontend/src/types/contracts.ts`

| Type | Lines |
| ---- | ----- |
| `Prediction` (direction, probability, expected_return, expected_volatility, prediction_interval) | 34–45 |
| `Decision` (actionable, direction, confidence, signal_strength, edge_ratio, net_return, position_size) | 48–66 |
| `ForecastResponse` (…, delivery_state, delivery_reason, delivery_warning, prediction, decision, data_quality, drivers, lineage) | 73–98 |
| `DriversResponse` (shap, macro_regime, rag.fed/boj, narrative, risks, event_sensitivity) | 150–169 |
| `RankedOpportunity` / `RankingResponse` | 174–197 / 200–213 |
| `StatisticalMetrics` / `EconomicMetrics` / `RegimePerformance` / `PerformanceDegradation` | 224–235 / 238–251 / 254–263 / 266–275 |
| `PerformanceResponse` | 278–293 |
| `PredictionLineage` (§7.5) / `DecisionLineage` (§7.6, `decision.rejection_reason`) | 372–383 / 386–447 |
| `InfrastructureStatus` / `IntelligenceStatus` / `DataQuality` / `StatusMetrics` / `StatusResponse` | 502–511 / 530–541 / 514–519 / 544–549 / 552–571 |

### 1.3 Services (endpoint adapters) — `frontend/src/services/*`

| Service | File:line | Endpoint (Layer 1 §3) |
| ------- | --------- | --------------------- |
| `getForecast(pair)` | `forecast.ts:12-14` | `GET /v1/fx/{pair}/forecast` |
| `getDrivers(pair)` | `drivers.ts:10-12` | `GET /v1/fx/{pair}/drivers` |
| `getRanking()` | `ranking.ts:11-13` | `GET /v1/fx/ranking` |
| `getPerformance(pair, period)` | `performance.ts:10-14` | `GET /v1/fx/performance/{pair}?period=` |
| `getStatus()` | `status.ts:12-14` | `GET /v1/status` |
| `apiClient` (base URL, timeout, retry) | `api.ts:47-54`, `api.ts:56-67` | transport only |

Gap services intentionally NOT implemented: `getForecastHistory`, `getHealth` (see CONTRACT_GAPS.md).

### 1.4 Hooks — `frontend/src/hooks/*`

| Hook | File:line | Service used |
| ---- | --------- | ------------ |
| `useForecast(pair)` | `useForecast.ts:12-16` | `getForecast` |
| `useDrivers(pair)` | `useDrivers.ts:11-15` | `getDrivers` |
| `useRanking()` | `useRanking.ts:11-15` | `getRanking` |
| `usePerformance(pair, period)` | `usePerformance.ts:11-15` | `getPerformance` |
| `useStatus()` | `useStatus.ts:11-15` | `getStatus` |
| `usePolling(fn, interval, enabled)` | `usePolling.ts:11-21` | infra only |

### 1.5 UI surface actually present (Prompt 0 scaffold)

| File | Evidence | Renders |
| ---- | -------- | ------- |
| `pages/ForecastPage.tsx:5-15` | placeholder | module text only — NO contract data |
| `pages/DriversPage.tsx:5-15` | placeholder | module text only |
| `pages/EvaluationPage.tsx:5-15` | placeholder | module text only |
| `pages/GlobalPage.tsx:5-15` | placeholder | module text only |
| `pages/StatusPage.tsx:5-15` | placeholder | module text only |
| `components/layout/Header.tsx:22-28,25-43` | VERIFIED UI | `system_status` + `timestamp` via `useStatus` (the ONLY implemented contract-consuming UI) |
| `components/layout/Sidebar.tsx:9-46` / `MainLayout.tsx:11-22` | nav/layout | no contract data |
| `components/common/NotAvailable.tsx:17-39` | gap renderer | `FEATURE_STATE.NOT_AVAILABLE`, `UNSUPPORTED_BY_CONTRACT`, `NO_FALLBACK_ALLOWED`, `NO_DERIVATION_ALLOWED` |
| `components/forecast|drivers|evaluation|global|status/` | **EMPTY** (`.gitkeep` only) | mockup modules not yet implemented |
| `utils/status.ts:14-40,46-74,80-94,104-107,117-120` | presentation-only maps | status/signal/delivery label+color (no derivation) |
| `utils/gaps.ts:11-18` | closed-registry lookup | feature state from `CONTRACT_GAP_MAP` |

Routing: `App.tsx:33-42` → 5 placeholder pages; no module components wired.

---

## 2. Traceability Matrix (mockup modules → frozen contract fields)

`PRED` = section + line in `docs/Product_specification/Layer_01.md`; `TS` = line in `frontend/src/types/contracts.ts`.
Component hop is ASSUMED (module components not implemented) for all except the Header row.

### 2.1 Forecast Dashboard — `useForecast` → `getForecast` → `/v1/fx/{pair}/forecast` → §7.1

| # | UI element | Hook/src | Contract field | PRED (§7.1) | TS | Status |
| - | ---------- | -------- | -------------- | ----------- | -- | ------ |
| 1 | Forecast direction | useForecast:12-16 / forecast.ts:12 | prediction.direction | 526-527 | 36 | VERIFIED (UI ASSUMED) |
| 2 | Probability | same | prediction.probability | 528 | 38 | VERIFIED (UI ASSUMED) |
| 3 | Expected return | same | prediction.expected_return | 529 | 40 | VERIFIED (UI ASSUMED) |
| 4 | Expected volatility | same | prediction.expected_volatility | 530 | 42 | VERIFIED (UI ASSUMED) |
| 5 | Prediction interval | same | prediction.prediction_interval.lower/.upper | 531 | 26-31,44 | VERIFIED (UI ASSUMED) |
| 6 | Delivery state | same | delivery_state (presentation: utils/status.ts:117-120) | 522 | 83 | VERIFIED (UI ASSUMED) |
| 7 | Delivery reason | same | delivery_reason | 523 | 85 | VERIFIED (UI ASSUMED) |
| 8 | Delivery warning | same | delivery_warning | 524 | 87 | VERIFIED (UI ASSUMED) |
| 9 | Timestamp / as-of | same | timestamp / as_of | 519-520 | 79/81 | VERIFIED (UI ASSUMED) |

### 2.2 Decision / Actionability (same forecast endpoint) — §7.1 `decision`

| # | UI element | Contract field | PRED | TS | Status |
| - | ---------- | -------------- | ---- | -- | ------ |
| 10 | Actionable flag | decision.actionable (consumed directly — never re-derived) | 535 | 50 | VERIFIED (UI ASSUMED) |
| 11 | Direction (LONG/SHORT/NEUTRAL) | decision.direction | 536 | 52 | VERIFIED (UI ASSUMED) |
| 12 | Confidence score | decision.confidence | 537 | 54 | VERIFIED (UI ASSUMED) |
| 13 | Signal strength | decision.signal_strength (presentation: utils/status.ts:104-107) | 538 | 56 | VERIFIED (UI ASSUMED) |
| 14 | Edge ratio | decision.edge_ratio | 539 | 58 | VERIFIED (UI ASSUMED) |
| 15 | Net return | decision.net_return | 540 | 60 | VERIFIED (UI ASSUMED) |
| 16 | Position size (supported) | decision.position_size — distinct from recommendation (G3) | 541 | 65 | VERIFIED (UI ASSUMED) |
| 17 | Rejection reason | NOT in §7.1 decision block; surfaced as `delivery_reason` (PRED 426 / §5 R1) and `lineage.decision.rejection_reason` (§7.6:719, TS:400) | 719 | 400 | CORRECTED (see §3) |
| 18 | Signal validity | NOT exposed; closest is `StatusResponse.intelligence.decision_validity` (§7.7:782, TS:538) | 782 | 538 | CORRECTED (see §3) |

### 2.3 Economic filter & costs (mockup)

| # | UI element | Contract field | Status |
| - | ---------- | -------------- | ------ |
| 19 | Spread cost | — | OPTIONAL GAP (absent from L1 §7; see GAPS EC-1) |
| 20 | Slippage cost | — | OPTIONAL GAP (EC-2) |
| 21 | Commission cost | — | OPTIONAL GAP (EC-3) |
| 22 | Required minimum edge | — | OPTIONAL GAP (EC-4) |

### 2.4 Drivers & Explanation — `useDrivers` → `getDrivers` → `/v1/fx/{pair}/drivers` → §7.2

| # | UI element | Contract field | PRED | TS | Status |
| - | ---------- | -------------- | ---- | -- | ------ |
| 23 | SHAP contributions | drivers.shap[] (feature, contribution, rank) | 558-560 | 103-110,158 | VERIFIED (UI ASSUMED) |
| 24 | Macro regime | drivers.macro_regime (risk/policy/growth/inflation) | 562-567 | 122-131,160 | VERIFIED (UI ASSUMED) |
| 25 | Fed sentiment | drivers.rag.fed.sentiment / .expectation_gap | 570-571 | 134-139,144 | VERIFIED (UI ASSUMED) |
| 26 | BoJ sentiment | drivers.rag.boj.sentiment / .expectation_gap | 571 | 146 | VERIFIED (UI ASSUMED) |
| 27 | Executive narrative | drivers.narrative | 574 | 164 | VERIFIED (UI ASSUMED) |
| 28 | Risks list | drivers.risks[] | 575 | 166 | VERIFIED (UI ASSUMED) |
| 29 | Event sensitivity | drivers.event_sensitivity[] | 576 | 168 | VERIFIED (UI ASSUMED) |
| 30 | Technical analysis summary | — | — | — | OPTIONAL GAP (G-05) |

### 2.5 Global / Ranking — `useRanking` → `getRanking` → `/v1/fx/ranking` → §7.3

| # | UI element | Contract field | PRED | TS | Status |
| - | ---------- | -------------- | ---- | -- | ------ |
| 31 | Ranking table | ranking.opportunities[] | 587-601 | 174-197,206 | VERIFIED (UI ASSUMED) |
| 32 | Top opportunity | ranking.top_opportunity | 603 | 208 | VERIFIED (UI ASSUMED) |
| 33 | Total actionable | ranking.total_actionable | 604 | 210 | VERIFIED (UI ASSUMED) |
| 34 | Total pairs | ranking.total_pairs | 605 | 212 | VERIFIED (UI ASSUMED) |
| 35 | Snapshot time / as-of | snapshot_timestamp / as_of | 584-585 | 202/204 | VERIFIED (UI ASSUMED) |
| 36 | Global regime | — (`/v1/fx/regime` endpoint has no response structure) | ~142,879 | gaps.ts:50 | OPTIONAL GAP (G4) |
| 37 | Regime alignment | — (no field in L1 §7) | — | — | OPTIONAL GAP (G-EC/RA) |
| 38 | Cross-correlation heatmap | — | — | — | OPTIONAL GAP (G-07) |
| 39 | Early warnings | — | — | — | OPTIONAL GAP (G-08) |
| 40 | Macro calendar | — | — | — | OPTIONAL GAP (G5 / G-09) |

### 2.6 Performance Dashboard — `usePerformance` → `getPerformance` → `/v1/fx/performance/{pair}?period=` → §7.4

| # | UI element | Contract field | PRED | TS | Status |
| - | ---------- | -------------- | ---- | -- | ------ |
| 41 | Directional accuracy | statistical.directional_accuracy | 618 | 226 | VERIFIED (UI ASSUMED) |
| 42 | AUC | statistical.auc | 619 | 228 | VERIFIED (UI ASSUMED) |
| 43 | Brier score | statistical.brier_score | 620 | 230 | VERIFIED (UI ASSUMED) |
| 44 | ECE | statistical.ece | 621 | 232 | VERIFIED (UI ASSUMED) |
| 45 | Log loss | statistical.log_loss | 622 | 234 | VERIFIED (UI ASSUMED) |
| 46 | Sharpe ratio | economic.sharpe_ratio | 626 | 240 | VERIFIED (UI ASSUMED) |
| 47 | Sharpe net | economic.sharpe_net | 627 | 242 | VERIFIED (UI ASSUMED) |
| 48 | Max drawdown | economic.max_drawdown | 628 | 244 | VERIFIED (UI ASSUMED) |
| 49 | Profit factor | economic.profit_factor | 629 | 246 | VERIFIED (UI ASSUMED) |
| 50 | Win rate | economic.win_rate | 630 | 248 | VERIFIED (UI ASSUMED) |
| 51 | Total return | economic.total_return | 631 | 250 | VERIFIED (UI ASSUMED) |
| 52 | Regime performance | regime_performance[] (.regime/.sharpe/.da/.count) | 634-641 | 254-263 | VERIFIED (UI ASSUMED) |
| 53 | Drift detected | degradation.drift_detected | 646 | 272 | VERIFIED (UI ASSUMED) |
| 54 | Drift severity | degradation.drift_severity | 647 | 274 | VERIFIED (UI ASSUMED) |
| 55 | Drift context (current/historical Sharpe) | degradation.current_sharpe / .historical_sharpe | 644-645 | 268/270 | VERIFIED (UI ASSUMED) |
| 56 | Calibration curve | — | — | — | OPTIONAL GAP (G-EC/CA) |
| 57 | Calibration status | — | — | — | OPTIONAL GAP (G-06) |

### 2.7 System Status — `useStatus` → `getStatus` → `/v1/status` → §7.7

| # | UI element | Contract field | PRED | TS | Component | Status |
| - | ---------- | -------------- | ---- | -- | --------- | ------ |
| 58 | System status | status.system_status | 764 | 554 | Header.tsx:25-27 (implemented) | VERIFIED |
| 59 | Status reason | status.reason | 765 | 556 | — | VERIFIED (UI ASSUMED) |
| 60 | Status timestamp | status.timestamp | 766 | 558 | Header.tsx:40-44 (implemented) | VERIFIED |
| 61 | Infrastructure status | status.infrastructure.{api,database,pipeline,cache} | 768-773 | 502-511 | — | VERIFIED (UI ASSUMED) |
| 62 | Data quality (intelligence) | intelligence.data_quality.overall / .status | 775-779 | 532/516,518 | — | VERIFIED (UI ASSUMED) |
| 63 | Model performance health | intelligence.model_performance | 780 | 534 | — | VERIFIED (UI ASSUMED) |
| 64 | Model drift health | intelligence.model_drift | 781 | 536 | — | VERIFIED (UI ASSUMED) |
| 65 | Decision validity | intelligence.decision_validity | 782 | 538 | — | VERIFIED (UI ASSUMED) |
| 66 | Safe mode state | intelligence.safe_mode_state | 783 | 540 | — | VERIFIED (UI ASSUMED) |
| 67 | Data freshness (metric) | status.metrics.data_freshness | 787 | 546 | — | VERIFIED (UI ASSUMED) |
| 68 | Prediction coverage (metric) | status.metrics.prediction_coverage | 788 | 548 | — | VERIFIED (UI ASSUMED) |
| 69 | Latest prediction time | status.latest_prediction | 791 | 566 | — | VERIFIED (UI ASSUMED) |
| 70 | Last ingestion time | status.last_successful_ingestion | 792 | 568 | — | VERIFIED (UI ASSUMED) |
| 71 | Next inference time | status.next_scheduled_inference | 793 | 570 | — | VERIFIED (UI ASSUMED) |

### 2.8 Lineage (deferred, structures defined) — §7.5 / §7.6

| # | UI element | Contract field | PRED | TS | Status |
| - | ---------- | -------------- | ---- | -- | ------ |
| 72 | Prediction lineage | lineage.{prediction,model,features,data,source} | 652-701 | 372-383 | VERIFIED (structure) — UI deferred (G9) |
| 73 | Decision lineage | lineage.{decision(…,rejection_reason),…policy,fusion} | 703-758 | 386-447 | VERIFIED (structure) — UI deferred (G9) |

---

## 3. Corrections — claims in the draft matrix that are NOT supported by the repository/spec

| Draft claim | Repository/spec reality | Resolution |
| ----------- | ----------------------- | ---------- |
| `ForecastResponse.forecast.direction` | Field is `prediction.*` (not `forecast.*`) — PRED 526-532, TS 34-45 | Rows 1–5 corrected to `prediction.*` |
| `ForecastResponse.regime.name` (Current regime, VERIFIED) | No `regime` field in §7.1/§7.3 responses; `/v1/fx/regime` has no response structure | OPTIONAL GAP (G4) |
| `decision.signal_validity` (VERIFIED) | Not a Layer 1 field; only `intelligence.decision_validity` (§7.7:782) | Corrected; row 18 |
| `decision.rejection_reason` (VERIFIED) | Only `delivery_reason` (§5 R1 / §7.1:523) and `lineage.decision.rejection_reason` (§7.6:719) | Corrected; row 17 |
| `economic_filter.{spread,slippage,commission,required_minimum_edge}` (VERIFIED) | No `economic_filter` block exists in L1 §7 | OPTIONAL GAPS EC-1…EC-4 |
| `data_quality.data_freshness` / `.prediction_coverage` (VERIFIED) | `DataQuality` = {overall, status} only; these live in `StatusResponse.metrics` (§7.7:786-789) | Corrected; forecast context = gap, status context = verified |
| `PerformanceResponse.calibration.calibration_curve` (VERIFIED) | No `calibration` block in L1 §7 | OPTIONAL GAP |
| 44 UI elements "VERIFIED" (draft summary) | 44 data paths verified, but ALL module components (ForecastSummary, ActionabilityPanel, SHAPChart, RAGPanel, RankingTable, MetricsSummary, …) are ASSUMED — not implemented (empty component dirs; pages are placeholders `pages/*.tsx:5-15`) | Honest status: VERIFIED contract/data path + ASSUMED UI component |
| Gap ID set G-01…G-09 (draft) | Repository authoritative registry is G1–G9 (`docs/Contract/CONTRACT_GAPS.md`, mirrored in `types/gaps.ts:41-54`) | GAP doc unified under G1–G9 |

## 4. Endpoint Verification

| Endpoint | Contract | Service | Status |
| -------- | -------- | ------- | ------ |
| `GET /v1/fx/{pair}/forecast` | §7.1 ForecastResponse | forecast.ts:12-14 | VERIFIED |
| `GET /v1/fx/{pair}/drivers` | §7.2 DriversResponse | drivers.ts:10-12 | VERIFIED |
| `GET /v1/fx/ranking` | §7.3 RankingResponse | ranking.ts:11-13 | VERIFIED |
| `GET /v1/fx/performance/{pair}?period=` | §7.4 PerformanceResponse | performance.ts:10-14 | VERIFIED |
| `GET /v1/status` | §7.7 StatusResponse | status.ts:12-14 | VERIFIED |
| `GET /v1/fx/{pair}/forecast/history` | §8 SLA only — no §7 structure | — | OPTIONAL GAP (G1) |
| `GET /v1/health` | §8 SLA only — no §7 structure | — | OPTIONAL GAP (G2) |
| `GET /v1/fx/regime` | §3/§10 data source — no §7 structure | — | OPTIONAL GAP (G4) |
| `GET /v1/fx/lineage/…/{id}` | §7.5/§7.6 structures defined | — (out of scope) | VERIFIED structure — UI deferred (G9) |

---

## 5. Tally (honest, evidence-based)

Counts are per the matrix above (rows are element/field granularity; the draft's "44 elements"
maps onto the finer-grained rows).

| Class | Count |
| ----- | ----- |
| Rows VERIFIED at the contract/data path (type + service + hook + endpoint + spec; component hop ASSUMED except Header) | 61 |
| — of which distinct supported mockup elements (§2.1–§2.7, incl. deferred lineage structure §2.8) | 44 |
| — of which Module UI components actually implemented (Header system-status indicator) | 1 |
| — of which Module UI components ASSUMED (mockup elements not yet in repo) | 43 |
| Rows rendering an OPTIONAL GAP state in-matrix (EC-1…EC-4, G-05, G4, RA, G-07, G-08, G5, calibration ×2, DF-P context) | 12 |
| — unified gap registry (see CONTRACT_GAPS.md: 9 canonical G1–G9 + 7 audit-surfaced) | 16 |
| BLOCKING GAPS | 0 |
| Total matrix rows | 73 |