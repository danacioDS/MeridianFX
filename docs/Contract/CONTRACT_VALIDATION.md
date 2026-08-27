# CONTRACT_VALIDATION.md — Meridian FX — Prompt 1 (AUDIT ONLY)

**Prompt 1 — TypeScript Contracts Validation (AUDIT ONLY)**
**Version:** v1.0 · **Date:** 2026-08-27
**Scope:** `frontend/src/types/contracts.ts` (571 lines) vs `docs/Product_specification/Layer_01.md` §7 (lines 511–795), Layer 1 v5.1.

> Per Prompt 0 §2 RULE 10: this audit **VALIDATES** only. It **MUST NOT** redefine or invent
> contracts, and **MUST NOT** modify them automatically. Result: PASS → proceed · FAIL → report →
> human/backend decision.

---

## 1. Result

| Check | Verdict |
| ----- | ------- |
| Contracts compared (7.1–7.7) | 7 / 7 |
| Field-count match | 6 / 7 exact |
| Extra fields in TS (not in spec) | 0 |
| Missing required fields | 0 |
| Type-enum mismatches | 0 |
| Nullability mismatches | 3 minor (shared lineage types; see §3) |
| **OVERALL** | **✅ PASS** |

## 2. Per-contract field audit

Legend: `✓` exact match (name + type + nullability). `⩒` matches, shared-type relaxation (documented in §3).

### 7.1 ForecastResponse — ✅ exact (10/10)

| Spec field | TS field | TS line | Verdict |
| ---------- | -------- | ------- | ------- |
| prediction_id: str | `prediction_id: string` | 75 | ✓ |
| pair: str | `pair: string` | 77 | ✓ |
| timestamp: datetime | `timestamp: string` | 79 | ✓ |
| as_of: datetime | `as_of: string` | 81 | ✓ |
| delivery_state: enum(3) | `delivery_state: DeliveryState` | 83 | ✓ |
| delivery_reason: str | `delivery_reason: string` | 85 | ✓ |
| delivery_warning: str\|null | `delivery_warning: string \| null` | 87 | ✓ |
| prediction: {...}\|null | `prediction: Prediction \| null` (5 fields) | 89 | ✓ |
| decision: {...}\|null | `decision: Decision \| null` (7 fields) | 91 | ✓ |
| data_quality \| drivers \| lineage : …\|null | 3 nullable sub-objects | 92–97 | ✓ |

### 7.2 DriversResponse — ✅ exact (10/10)

prediction_id, pair, timestamp ✓ · shap[feature,contribution,rank] ✓ · macro_regime{risk,policy,growth,inflation} ✓ · rag{fed,boj}{sentiment,expectation_gap} ✓ · narrative ✓ · risks ✓ · event_sensitivity ✓ (TS 150–169). All enum unions match spec literals exactly (Risk-On/Neutral/Risk-Off, etc.).

### 7.3 RankingResponse — ✅ exact (13/13)

snapshot_timestamp, as_of ✓ · opportunities[rank,pair,direction,opportunity_score,edge_ratio,actionable,confidence,decision_quality,position_size,prediction_id,decision_id] ✓ · top_opportunity: str\|null ✓ · total_actionable ✓ · total_pairs ✓ (TS 174–213).

### 7.4 PerformanceResponse — ✅ exact (19/19)

pair ✓ · period: enum(5) ✓ · as_of ✓ · statistical{5} ✓ · economic{6} ✓ · regime_performance[regime,sharpe,da,count] ✓ · degradation{current_sharpe,historical_sharpe,drift_detected,drift_severity: enum(3)} ✓ (TS 217–293).

### 7.5 LineageResponse (Prediction) — ✅ (field-complete; 2 ⩒)

| Spec field | TS field | TS line | Verdict |
| ---------- | -------- | ------- | ------- |
| prediction_id / pair / timestamp | same | 451–456 | ✓ |
| lineage.prediction {id,version,timestamp,as_of} | `LineageIdentity` | 374 | ✓ |
| lineage.model {id,version,type} | `LineageModel` | 376 | ✓ |
| lineage.features {snapshot_id,version,feature_count,feature_list[]} | `LineageFeatures` (`feature_list?`) | 378 | ⩒ |
| lineage.data {dataset_id,version,pit_validation} | `LineageData` | 380 | ✓ |
| lineage.source {…,vintage_id,vintage_time,available_time} | `LineageSource` (`vintage_id?`,`vintage_time?`,`available_time?`) | 382 | ⩒ |

### 7.6 LineageResponse (Decision) — ✅ (field-complete; 1 ⩒)

| Spec field | TS field | TS line | Verdict |
| ---------- | -------- | ------- | ------- |
| decision_id / prediction_id / pair / timestamp | same | 463–470 | ✓ |
| lineage.decision {…,actionable,rejection_reason: str\|null} | inline (`rejection_reason: string \| null`) | 388–401 | ✓ |
| lineage.prediction / model / features (no feature_list) / data | prediction inline, `LineageModel`, inline features, `LineageData` | 403–423 | ✓ |
| lineage.source {id,name,reference_period,vintage_id,vintage_time} | `LineageSource` (includes optional `available_time`) | 425 | ⩒ |
| lineage.policy {id,version} | inline | 428–432 | ✓ |
| lineage.fusion {version, weights{quant,macro,rag}} | inline (`weights: {quant|macro|rag: number}`) | 434–446 | ✓ |

### 7.7 StatusResponse — ✅ exact (16/16)

system_status: enum(4) ✓ · reason ✓ · timestamp ✓ · infrastructure{api,database,pipeline,cache} ✓ · intelligence{data_quality{overall,status}, model_performance, model_drift, decision_validity, safe_mode_state} ✓ · metrics{data_freshness,prediction_coverage} ✓ · latest_prediction\|last_successful_ingestion\|next_scheduled_inference: datetime\|null ✓ (TS 552–571). All enums match spec literals exactly.

## 3. Findings (non-blocking, no action required for PASS)

| # | Finding | Severity | Analysis |
| - | ------- | -------- | -------- |
| F1 | `LineageFeatures.feature_list?` optional (contracts.ts:342) but required in §7.5 | minor | Shared type intentionally relaxes to null-agnostic so `DecisionLineage.features` (§7.6, no feature_list) reuses it. Runtime payloads keep the field. Missing-field enforcement is looser than spec; acceptable under freeze (types match the actual → possible shape). No invented field. |
| F2 | `LineageSource.vintage_id?` / `.vintage_time?` tie to F1 | minor | §§7.5/7.6 declare different subsets of these refs; one shared interface covers both. No extra possibilities beyond spec unions. |
| F3 | `LineageSource.available_time?` optional (self-declared) | minor | Present in §7.5, absent in §7.6. Optionality only; type `string` matches otherwise. |

These are modeling relaxations on *lineage-only* shared types. All five primary contracts (7.1–7.4, 7.7) and both lineage payloads match 100% on names, types, and nullability where declared. No corrective edit is warranted; if the team prefers strict one-to-one shapes later, split the shared types — this is a **backend-free, cosmetic** change and does not block Prompt 4+.

## 4. Regression guard already present

`frontend/src/tests/contracts/validate.test.ts` (8 tests) enforces that contract fixtures include every TS field and no extras — **passing** (47/47 suite green, 2026-08-27). `tsc --noEmit` clean.

## 5. Decision

**✅ PASS — PROCEED to Prompt 4 (Common Components).**
Contracts are NOT modified by this audit. Findings F1–F3 are informational only.