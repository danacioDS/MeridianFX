# Meridian FX — Repository Report

**Date:** 2026-10-02 · **HEAD:** `27746d2` "fix(frontend): remove unused actionable param in _buildSummary" (2026-09-18) · **History:** 231 commits (2026-08-25 → 2026-09-18) · **Latest tag:** `v2.7.5` (`f45b097`) — HEAD is **37 commits** past the tag · **Working tree:** `report.md` + `architecture.md` modified (uncommitted), `comandos.md` + `informe.md` untracked · **⚠ HEAD is detached** (no branch checked out), although it equals `origin/main`.
**Verified on 2026-10-02:** backend `pytest -q` → **180 passed** (20 files, 31.5 s) · frontend `npm test` → **56 passed / 7 files** · `npm run build` (`tsc --noEmit && vite build`) → **PASS**, 1,501.61 kB / 305.81 kB gzip · CI backend job `pytest backend/layer4/tests/` → **exit 5, 0 tests collected** · live smoke via `TestClient` on 9 endpoints (results inline, §6).
**Prior report:** 2026-09-16 (HEAD `f78af89`).

This document is an audit of the repository **as it stands today**: what it is, how it is governed, what is verified, and — most importantly — **which claims the current evidence does and does not support**. Every number below was re-measured on 2026-10-02; the previous report's numbers were not carried over unless re-verified.

---

## 0. Executive verdict

The **software** is in materially better shape than the **evidence** behind it.

- **Engineering surface: healthy.** 9 canonical pairs served end-to-end, canonical ranking (`/v1/fx/ranking`, `total_pairs=9`, 4 actionable), 180 backend tests green, frontend typecheck/build/tests green, eligibility gate and risk engine working, PIT/temporal scaffolding in place.
- **Evidentiary surface: not publishable.** The macro feature that differentiates the model (`policy_diff`, feature 24/24 of every canonical model) is **semantically wrong for 5 of 9 currencies and absent for 3 of 9**; in the one artifact that recorded it, it was **constant** (`mean = min = max = −0.345`, `std = 0.0`). The only quality metrics in the promotion registry show **7 of 10 models below random** (AUC < 0.5). The decision horizon served to clients (**5 d**) does not match the horizon the models were trained on (**10 d**).
- **Consequence:** the platform may legitimately be described as *"a traceable, explainable, contract-governed decision pipeline over FX data"*. It may **not** be described as *"a system whose forecasts demonstrate validated predictive value"*, and no external claim should rest on the current `policy_diff` contribution, the `edge_ratio` / `position_size` numbers, or the registry AUCs until §12 Wave 0 lands.
- **Three decisions are needed from the owner** (§12.0): (a) freeze external performance claims, (b) decide whether `policy_diff` is re-sourced or removed, (c) declare one registry authoritative.

**Delta since the previous report:** only **2 commits** landed (`da77805`, `27746d2`), both frontend, both closing the previous report's #1 red item — but *at the client*, not the server. The materially new content of this cycle is not code: it is the macro-data audit recorded in `informe.md` (2026-10-01), whose central claim I re-verified against the source code and against live runtime logs (§3).

---

## 1. What this is

**Meridian FX** is an FX intelligence product built on one principle:

> *"Meridian does not merely produce predictions. It produces actionable, traceable, explainable, and measurable financial intelligence."*

It answers its product questions over a **9-pair canonical universe** (USD/JPY, EUR/USD, GBP/USD, USD/CNY, USD/MXN, USD/BRL, USD/ARS, USD/BOB, USD/CHF) with a 5-day decision horizon and 30/60/90-day forecast surfaces:

| Question | Surface |
| --- | --- |
| What is happening in the market? | Global Overview + Market page |
| What does Meridian expect? | Market / Decision pages (canonical forecast) |
| Why? | Decision page (SHAP + economic breakdown) |
| Is it worth acting? | Decision page (economic filter, gates, actionable flag) |
| What could invalidate the signal? | Decision page (signal validity / hard gates) |
| Is the pair's regime trustworthy? | Global page (regime-divergence banner + panel) |
| How risky is it / how good has Meridian been? | Risk page / performance surface |

---

## 2. What changed in this cycle (2026-09-16 → 2026-10-02)

Two commits, both frontend. The important consequence is architectural, not cosmetic.

1. **`da77805` — the Global intelligence surface now reads the canonical ranking.** `useMarketIntelligence.ts` (+302 lines) stopped calling `/v1/market-intelligence` and instead adapts `GET /v1/fx/ranking` into the `MarketIntelligence` shape client-side. The hook's own docstring records the reason: the legacy endpoint *"returned 0 pairs in production after the promotion gate"*.
   - ✅ **Closes the previous report's #1 red item** — the Global hero no longer contradicts the 9-pair ranking.
   - ⚠️ **But the fix landed in the wrong layer.** The legacy backend endpoint is untouched (`backend/layer1/routers/intelligence.py:16,22,429` still constructs `RankingEngine`) and is now **unconsumed by the client**, while ~300 lines of *business* aggregation (opportunity-score shaping, decision view, context text) now live in the browser. Two consequences: the backend keeps serving a surface nobody reads, and the same logic now exists in two languages with no shared contract. See **F-07**.
2. **`27746d2`** — removed an unused `actionable` parameter in the hook's `_buildSummary` (lint-level cleanup left over from #1).
3. **New, uncommitted:** `informe.md` (2026-10-01) — Spanish technical audit of the macro chain. Its central finding is **confirmed here** (§3). The file is untracked and **truncated mid-sentence** at line 445 (`policy_diff std  =_`); it should not be cited as a closed document until finished.
4. **No code change** to the backend, the training pipeline, the providers, the registries, the CI, or the governance ledgers in 16 days.

### 2.1 Corrections to the previous report

Errors found while re-verifying. Listed because a report that only accumulates findings is not auditable.

| Previous claim | Reality (verified 2026-10-02) |
| --- | --- |
| "Canonical Logistic_24 … **5-day forward target**" | ❌ All 10 artifacts record `horizon = 10`; `train_canonical_model.py:24` and `train_multi_pairs.py:35` both set `HORIZON = 10`. The API serves `horizon_days = 5`. (**F-05**) |
| "Ranking is canonical 9-pair … closes #1 red item" | ⚠️ True for `/v1/fx/ranking` only. `/v1/market-intelligence` still ran the legacy engine and returned `total_pairs = 1` — and still does (**F-07**) |
| "Registry drift … 1 ACTIVE vs 10 ACTIVE" | ✅ Correct, and materially worse than stated: **7 of the 10 models have AUC < 0.5**; only USD/CHF (0.733), USD/BRL (0.520), USD/ARS (0.513) are above random (**F-03**) |
| "Forecast cache now writes … cold-starts no longer amplified" | ⚠️ Cache writes, but `/v1/status` reports `prediction_coverage = 0.1` and `model_drift = CRITICAL` because the *registry* gate — not the cache — is what defines "active" |
| "180 tests / 56 frontend tests / 1,494.20 kB" | ✅ Re-measured: 180 / 56, bundle now **1,501.61 kB** (grew with the client-side adapter) |
| "HEAD `f78af89`, in sync with `origin/main`" | ⚠️ HEAD advanced to `27746d2` and is **detached** (**F-17**) |

---

## 3. Model & data credibility (promoted to top tier this cycle)

This section did not exist as a top-level concern in previous reports. It is now the dominant risk, and every claim in it is reproducible from the commands in §13.

### 3.1 The `policy_diff` feature is not what its name says

Every canonical model uses 24 features: 23 technical + **`policy_diff`** (`models/canonical/metadata_20260908_172009.json`). The contract is `policy_diff = base_policy_rate − quote_policy_rate`. The PIT alignment mechanism is **correct** — `MacroDifferentialProvider.calculate_historical` uses `merge_asof(direction="backward")` (`backend/layer2/data/macro/differential_provider.py:304,311`). The defect is upstream, in what the providers call `policy_rate`:

| Currency | Provider | Underlying series | Rows (2023-01-01→2026-08-31) | Verdict for `policy_rate` |
| --- | --- | --- | ---: | --- |
| USD | `FREDProvider` | `DFF` (Federal Funds Rate) | 1339 | ✅ valid |
| EUR | `EuroProvider` | ECB Deposit Facility Rate | 1339 | ✅ valid |
| GBP | `UKProvider` | `IRLTLT01GBM156N` — **long-term** rate | 44 | 🔴 mislabeled |
| JPY | `JapanProvider` | `IRLTLT01JPM156N` — **long-term** rate | 44 | 🔴 mislabeled |
| CHF | `SwitzerlandProvider` | `IRLTLT01CHM156N` — **long-term** rate | 44 | 🔴 mislabeled |
| MXN | `MexicoProvider` | `IRLTLT01MXM156N` — **long-term** rate | 36 | 🔴 mislabeled |
| BRL | `BrazilProvider` | `INTDSRBRM193N` — **long-term** rate | 44 | 🔴 mislabeled |
| CNY | `ChainCNYProvider` | CNBS/NBS → World Bank | 0 | 🟠 no history |
| ARS | `ArgentinaProvider` | FRED → HTTP 400 | 0 | 🟠 no history |
| BOB | `BoliviaProvider` | — | 0 | 🟠 no history |

The mislabeling is explicit in the code, not an accident of mapping: `providers/uk.py:5` reads *"IRLTLT01GBM156N: Long-term interest rates (**proxy** para policy_rate)"*, and `get_policy_rate` returns `reason="Long-term rates como policy_rate para UK"` (`uk.py:124`; identical pattern at `japan.py:124`, `switzerland.py:124`).

Three of the nine canonical pairs therefore carry a feature that means something different from training to inference, and three carry **no macro signal at all** (`policy_diff` → `None`, absorbed by the pipeline's `SimpleImputer(median)`).

**The correct providers already exist in the repository and are unused for this purpose:** `SNBPolicyRateProvider` (SNB official API, `snboffzisa`) in `providers/snb_policy.py`, and `BanxicoProvider` (`SF43718`, target rate) in `providers/banxico.py`. BoE / BoJ / BCB official sources do not.

### 3.2 In the one artifact that recorded it, `policy_diff` was constant

`models/canonical/logistic_24_extended_20260908_180112.joblib` → `policy_diff_stats = {mean: −0.345, std: 0.0, min: −0.345, max: −0.345, current_z_score: 0.0}`. A feature with zero variance carries zero information; that model was fitted with a constant 24th feature. The trainer corroborates it: `train_canonical_model_extended.py:133` hardcodes `current_policy = -0.345`.

The 9 per-pair artifacts record **no** `policy_diff_stats` and **no** `training_period` for 4 of them — i.e. the artifacts that actually serve production carry **no feature-provenance metadata at all** (**F-02**).

### 3.3 Registry metrics: the promotion gate's own numbers are mostly worse than random

`backend/models/registry.json` / `models/registry.json` (same 10 `model_id`s):

| Model | AUC | n | vs random (0.5) |
| --- | ---: | ---: | --- |
| USD/CNY xgboost | 0.380 | 319 | 🔴 −0.120 |
| USD/JPY xgboost | 0.408 | 301 | 🔴 −0.092 |
| GBP/USD xgboost | 0.430 | 319 | 🔴 −0.070 |
| USD/MXN xgboost | 0.437 | 319 | 🔴 −0.063 |
| USD/BOB xgboost | 0.437 | 319 | 🔴 −0.063 |
| USD/JPY logistic | 0.448 | 301 | 🔴 −0.052 |
| EUR/USD xgboost | 0.450 | 200 | 🔴 −0.050 |
| USD/ARS xgboost | 0.513 | 319 | 🟡 +0.013 |
| USD/BRL xgboost | 0.520 | 319 | 🟡 +0.020 |
| USD/CHF xgboost | **0.733** | 319 | 🟢 +0.233 |

Two observations. First, the gate **did** work as a filter — it demoted 9 of 10 models and left only the one meaningfully above random, which is why `/v1/status` reports `DEGRADED` / `prediction_coverage = 0.1`. Second, the surviving model's 0.733 comes from `n = 319` with **no walk-forward or holdout validation attached to it**; `research_walkforward*_results.json` and `research_validation_summary.csv` exist but are not bound to the promoted artifact. Four registry entries carry suspiciously round metrics (0.45 / 0.43 / 0.42 / 0.44), consistent with the hardcoded-metrics pattern still present in `layer3/experiments/run.py`.

### 3.4 The served horizon is not the trained horizon

| | Value | Source |
| --- | --- | --- |
| Trained target | `HORIZON = 10` business days | `train_canonical_model.py:24`, `train_multi_pairs.py:35`, `train_canonical_model_extended.py:33`; all 10 artifacts store `horizon: 10` |
| Served decision | `horizon_days = 5` | `PipelineBridge.evaluate_pair(horizon_days=5)`, `canonical` + `ranking` routers |
| Reported to client | `artifact.horizon_days = 5` | live response, 2026-10-02 |

A model trained to predict the 10-day direction is being consumed and **labelled** as a 5-day decision. Either the horizon must become 10 everywhere, or the models must be retrained at 5.

### 3.5 The economic layer produces non-economic numbers

Live `GET /v1/canonical/USD/CHF/decision` (2026-10-02, `horizon_days = 5`):

```
direction SHORT · confidence 0.641 · actionable true · gate all_passed true
directional_gross_return 63.42   net_return 56.93   edge_ratio 5.69
required_minimum_edge   10.00    position_size 121,655 (base 100,000 × edge 2.0)
signal_validity DEGRADED · risk 42.8 MODERATE · macro_data_status PARTIAL
```

A **63% expected move in 5 days** on USD/CHF is not a forecast; it is the formula at `backend/layer2/engine.py:384` — `expected_return = (2p − 1) · volatility · (horizon_days/365)^0.5` — i.e. a probability rescaled by volatility, with the code's own comment conceding it is *"escalado de volatilidad, no predicción multi-horizonte"*. Because `edge_ratio` and `position_size` are derived from it, the **entire actionability layer inherits the distortion**: the pair passes `required_minimum_edge = 10.0` by an order of magnitude. This is the single largest gap between what the UI says and what the number means (**F-08**).

Two further runtime inconsistencies from the same response:

- `macro_data_status = {policy_differential: null, quote_rate: null, status: "PARTIAL", base_rate: 3.88}` while the engine logged `PIT policy_diff USD/CHF` from a CHF "rate" — **two macro paths disagree** about the same pair in the same request (**F-20**).
- `fusion = {weights: {quant: 0.5, macro: 0.3, rag: 0.2}, fusion_score: −0.49799}` with `signals = {quant: −0.9960, macro: 0.0, rag: 0.0}`. −0.9960 × 0.5 = −0.49799 exactly: **the declared macro and RAG weights contribute nothing** because their inputs are hardcoded 0.0. The weights are decorative (**F-22**).

### 3.6 Runtime confirmation of the macro chain (live log, 2026-10-02)

```
PIT policy_diff GBP/USD:  0.277150 (GBP=4.9886, USD=3.8800)   ← GBP = FRED long-term rate
PIT policy_diff EUR/USD: -0.345000 (EUR=2.5000, USD=3.8800)   ← EUR = ECB DFR (real)
No hay datos de policy rate para USD/CNY                       ← 3 currencies empty
```

---

## 4. Repository layout

```
MeridianFX/
├── .github/workflows/ci.yml          GitHub Actions — backend compile + `pytest backend/layer4/tests/` (0 tests,
│                                    exit 5), frontend `npm run build` (includes tsc) + `npm test`
├── .pre-commit-config.yaml           hygiene hooks (large-file 500 kB, EOF, whitespace, yaml, toml)
│                                    + local `pytest -q` gate (always_run)
├── pytest.ini                        root discovery: testpaths=backend/tests, pythonpath=.,backend,backend/src
├── docs/                             frozen specs + governance + model_selection + divergence/README.md
├── backend/
│   ├── layer1/                       FastAPI delivery API — 13 routers, dependencies.py (shared PipelineBridge),
│   │                                2 adapters, llm/, utils/pair_normalizer.py; dead: data/forecast_data.py, decision/
│   ├── layer2/                       live engine — engine.py (lazy Logistic_24 + policy_diff), pipeline_bridge.py,
│   │                                data/ (yahoo/twelve/alpha_vantage/fred) + data/macro/ (23 provider modules),
│   │                                features/, explainers/shap_explainer.py, models/, narrative/ (SQLite LLM),
│   │                                status/, quality/pit_adapter.py, ranking/ (legacy, still alive)
│   ├── layer3/                       research — artifacts, evaluation (walk_forward healthy; run_benchmarks broken),
│   │                                experiments (E0–E7, hardcoded), macro/regime, models (arima unrunnable),
│   │                                rag/ (keyword scorer), research_gate
│   ├── layer4/                       data quality — quality/pit_validator.py (PIT-1…PIT-7), config/policies.py,
│   │                                lineage/models.py, tests/pit_tests.py (compiles, undiscovered)
│   ├── src/meridian_fx/decision/     contract-governed Decision Engine (8-stage + KI-009 gate + RiskEngine),
│   │                                contracts/ (temporal, exchange_regime), divergence/, Stub* L4 registries
│   ├── models/                       10 xgboost/logistic .pkl + registry.json (10 entries, ALL active=true)
│   └── tests/                        20 files, 180 tests
├── models/                           canonical/ (10 Logistic_24 .joblib + 2 metadata json), experimental/,
│                                    registry.json (10 entries, 1 active: USD/CHF)
│                                    + registry.json.backup_20260914_140136
├── Dockerfile                        python:3.12-slim; COPY models/ + backend/; PYTHONPATH=/app/backend:/app;
│                                    MERIDIAN_MODEL_DIR=/app/models (⚠ zero consumers); EXPOSE 8080; PORT-aware CMD
├── render.yaml                       Render Docker service; healthCheckPath /health; FRED/GROQ/AV/TWELVE keys
│                                    (⚠ no ADMIN_TOKEN)
├── runtime.txt · start.sh · stop.sh
├── train_models.py (deprecated) · train_canonical_model{,_extended}.py · train_multi_pairs.py
├── train_experimental_models.py · evaluate_all_pairs.py · final_holdout.py
├── research_gate.py · research_validation_* · research_walkforward*.py (+ 7 *_results.json) · shadow_test*.py
├── monitor_daily.py · monitor_model.py · test_macro.py · test_pit.py
├── STABLE.md                         stable registry — current: v2.7.5 @ f45b097 (37 commits behind HEAD)
├── KNOWN_ISSUES.md                   authoritative debt ledger: KI-001…KI-009, A3, A4, P1, B, Stub L4, Resolved
├── scripts/                          audit_consistency.py · audit_registry.py · apply_gate.py
├── cache/ · logs/ · data/ · venv/    runtime state (gitignored)
├── frontend/                         React 18 + TS 5 + Vite 5 (5174) + Tailwind 3 + TanStack Query 5
│   ├── src/pages/                    Global · Market · Macro · Risk · Decision · About (+ historical/)
│   ├── src/hooks/                    12 hooks + index.ts
│   ├── src/services/                 api.ts (axios, retry/backoff) + forecast/ranking/performance/status
│   ├── src/types/                    contracts.ts (Layer 1 §7 mirror), gaps.ts (G1–G5)
│   └── .env*                         on disk, untracked; VITE_API_URL supplied by Cloudflare at build time
├── informe.md                        ⚠ UNTRACKED, truncated (line 445) — macro/policy_diff audit, 2026-10-01
├── comandos.md                       ⚠ UNTRACKED dev cheat sheet, not gitignored
├── report.md                         this document · architecture.md — system architecture (2026-10-02)
└── .env                              runtime secrets, gitignored
```

**Working-tree hygiene:** HEAD `27746d2` == `origin/main` but **detached**; 2 tracked files modified (the two docs, both uncommitted), 2 untracked (`informe.md`, `comandos.md`), neither ignored. Ignored noise: `venv/`, `backend/venv/`, `cache/`, `logs/`, `dist/`, `__pycache__/`.

---

## 5. Findings register

Severity: **BLOCKER** = invalidates published claims about model quality · **HIGH** = wrong behaviour visible to users or to CI · **MEDIUM** = correctness/consistency debt · **LOW** = hygiene.

| ID | Sev | Finding | Evidence |
| --- | --- | --- | --- |
| **F-01** | 🔴 BLOCKER | `policy_diff` = long-term interest rate for GBP/JPY/CHF/MXN/BRL, absent for CNY/ARS/BOB. Feature does not mean what it means in training docs | `providers/{uk,japan,switzerland,mexico,brazil}.py:5,124`; §3.1 |
| **F-02** | 🔴 BLOCKER | `policy_diff` was **constant** (std 0.0) in the extended canonical model; 4 of 9 serving artifacts carry no `training_period`/`policy_diff_stats`; trainer hardcodes `-0.345` | `logistic_24_extended_*.joblib`; `train_canonical_model_extended.py:133` |
| **F-03** | 🔴 BLOCKER | 7 of 10 registry models have AUC < 0.5; the 3 above random have no walk-forward validation bound; 4 entries have round placeholder metrics | §3.3 |
| **F-05** | 🟠 HIGH | Trained horizon 10 d, served and labelled 5 d | `train_*.py:24/35/33`; live `artifact.horizon_days` |
| **F-08** | 🟠 HIGH | `expected_return` is a volatility rescaling, not a return forecast → `net_return 56.9`, `edge_ratio 5.69`, `position_size 121,655` on a 5-day horizon; the whole actionability layer inherits it | `engine.py:381-384`; live USD/CHF decision |
| **F-04** | 🟠 HIGH | Registry split-brain: `backend/models/registry.json` 10 active vs root `models/registry.json` 1 active → `/v1/status` DEGRADED, `prediction_coverage 0.1`, `model_drift CRITICAL`; legacy ranking sees 1 pair | §6.2; `engine.py:24` |
| **F-09** | 🟠 HIGH | CI backend job collects **0 tests** (exit 5); the 180-test suite has no CI coverage | `.github/workflows/ci.yml`; reproduced |
| **F-07** | 🟡 MED | Global intelligence derived **client-side** from `/v1/fx/ranking` (+302 lines); `/v1/market-intelligence` still legacy (`total_pairs = 1`) and now unconsumed → duplicate business logic across languages, dead server surface | `useMarketIntelligence.ts:1-380`; `intelligence.py:16,22,429` |
| **F-22** | 🟡 MED | Fusion declares weights quant 0.5 / macro 0.3 / rag 0.2 but macro and rag signals are hardcoded `0.0` → fusion == quant | live decision `fusion`/`signals` |
| **F-20** | 🟡 MED | Two disagreeing macro paths in one request: `macro_data_status.quote_rate = null` while the engine computed `policy_diff` for the same pair | live decision + engine log |
| **F-06** | 🟡 MED | Artifact mislabels the running model: `model_id: "logistic_USD_CHF"`, `model_version: "logistic-v1.0"` while `Logistic_24` canonical is executing | live `artifact` block; extends KNOWN_ISSUES P1 |
| **F-10** | 🟡 MED | `MERIDIAN_MODEL_DIR` has **zero** consumers; model paths hardcoded and CWD-relative (9 paths, duplicated at `engine.py:51-59` and `159-167`) | grep across `backend/**/*.py` |
| **F-11** | 🟡 MED | KI-002 residual: wall-clock `as_of` fallback; `input_available_times = [as_of]` makes PIT-2 vacuously true; VIX timestamps synthetic | KNOWN_ISSUES KI-002-A/B/C |
| **F-12** | 🟡 MED | Canonical pipeline runs 3 `Stub*` L4 registries (fixed 0.90 / 3.0 / 0.05) → "data_quality: good" is a constant | `layer1/dependencies.py` |
| **F-13** | 🟡 MED | `forecast_eligibility` absent from the frontend decision contract → RESTRICTED vs INSUFFICIENT_EDGE indistinguishable to users | `frontend/src/hooks/useCanonicalDecision.ts` |
| **F-14** | 🟡 MED | Layer 3 tail broken: `run_benchmarks.py:18` (`engine.xgb_model`), `arima.py` needs `statsmodels` (absent from `requirements.txt` and the env), `experiments/run.py` hardcoded | reproduced |
| **F-15** | 🟡 MED | LLM partial: narrative via `LLMFallbackManager` only; `EconomicInterpreter` unimported; `/interpretation?include_macro` hardcoded | `layer1/llm/` |
| **F-16** | 🟡 MED | `render.yaml` declares no `ADMIN_TOKEN` → `POST /narrative/regenerate` returns 503 in production | `render.yaml` vs `narrative.py:55-57` |
| **F-19** | 🟡 MED | Ledger staleness: `KNOWN_ISSUES.md` item **B** still "deferred to v3.0" although `57566db` fixed the endpoint; `STABLE.md` 37 commits behind; `README.md` header still "v2.7 … tag v2.7 pendiente" and half in Spanish; `informe.md` truncated and untracked | §8 |
| **F-18** | ⚪ LOW | Frontend debt: 4 raw-`fetch` hooks (no retry/backoff), `usePolling` orphaned, bundle 1,501.61 kB unminified (warning suppressed), no code splitting | `use{Price,Ranking,MarketIntelligence,ForecastDashboard}.ts` |
| **F-17** | ⚪ LOW | **HEAD detached** — the last 2 commits exist only as a detached pointer; a `git checkout` would orphan them | `git status -sb` |
| **F-21** | ⚪ LOW | Unreachable dead code after `return`: `engine.py:122-127` (duplicate print + 3× `return None`) | `engine.py` |
| **F-23** | ⚪ LOW | Simulated/hardcoded remnants: `/historical` random fallback, `/performance` derived `ece`/`max_dd`/`regime`, FRED simulated without key, dead `layer1/data/` + `layer1/decision/` | grep |

---

## 6. Backend

### 6.1 Layer 1 — FastAPI delivery API (13 routers, deployed)

| Method | Path | Notes | Health (2026-10-02) |
| --- | --- | --- | --- |
| GET | `/` , `/health` | root, health | ✅ `{"status":"healthy"}` |
| GET | `/v1/status` | real `StatusEngine` | ⚠️ `DEGRADED`, `model_drift CRITICAL`, `prediction_coverage 0.1`, `database degraded` |
| GET | `/v1/fx/ranking` | **canonical 9-pair** via shared `PipelineBridge`, `asyncio.gather` | ✅ `total_pairs=9`, **4 actionable** |
| GET | `/v1/canonical/{pair}/decision` | `DecisionPipeline`, VIX real, 3 Stub registries, KI-009 | ✅ 200; 6 ELIGIBLE / 3 gated |
| GET | `/v1/canonical/{pair}/risk` | `RiskEngine`, computed for RESTRICTED too | ✅ 9/9 |
| GET | `/v1/canonical/{pair}/narrative` | cache-first, SQLite, no TTL, Groq primary | ✅ |
| POST | `/v1/canonical/{pair}/narrative/regenerate` | needs `X-Admin-Token` | ⚠️ 503 in prod (F-16) |
| GET | `/v1/fx/{base}/{quote}/forecast` | `DecisionEngine.get_forecast` → Logistic_24, exposes `last_date` | ✅ live |
| GET | `/v1/fx/performance/{pair}?period=` | registry metrics + derived fields | ⚠️ derived (F-23) |
| GET | `/v1/fx/{pair}/historical` | layer2 data + features | ⚠️ random-synthetic fallback |
| GET | `/v1/fx/interpretation?pair=&include_macro=` | inline rule-based narrative | ⚠️ `include_macro` hardcoded |
| GET | `/v1/fx/{pair}/price?period=` | live spot/history + XGBoost signal | ✅ live |
| GET | `/v1/fx/{pair}/forecast-dashboard` | 30/60/90d + macro | ⚠️ `model.version = "v1.0"` ≠ `Logistic_24` (P1) |
| GET | `/v1/fx/{pair}/model-comparison` | Layer 3 `evaluate_expanding` (in-memory cache) | ✅ 200 (slow) |
| GET | `/v1/fx/{pair}/regime-divergence` | rolling ARIMA(1,0,1), z-score, interpretation | ✅ |
| GET | `/v1/market-intelligence` | **legacy `RankingEngine`** | ⚠️ `source.total_pairs = 1`, `total_actionable = 0` — and now unconsumed by the FE (F-07) |

### 6.2 The two "truths" that disagree (measured, same process, same minute)

| Question | Canonical path | Legacy path |
| --- | --- | --- |
| How many pairs does Meridian cover? | `/v1/fx/ranking` → **9** | `/v1/market-intelligence` → **1** |
| How many are actionable right now? | **4** (EUR/USD, USD/MXN, GBP/USD, USD/CHF) | **0** |
| What does the system self-report? | — | `"The decision layer is currently SELECTIVE … none currently satisfies the full set of economic criteria"` |

The Global page no longer shows the legacy answer (that was `da77805`), but the endpoint still publishes it, and any direct consumer — or the next frontend refactor — inherits the contradiction.

Ranking snapshot (2026-10-02), for the record:

```
1 EUR/USD  0.7992 actionable  conf 0.665      6 USD/BRL  0.2502 —  conf 0.469
2 USD/MXN  0.7969 actionable  conf 0.662      7 USD/CNY  0.0000 RESTRICTED
3 GBP/USD  0.7350 actionable  conf 0.558      8 USD/ARS  0.0000 RESTRICTED
4 USD/CHF  0.7252 actionable  conf 0.542      9 USD/BOB  0.0000 RESTRICTED
5 USD/JPY  0.2638 —           conf 0.466
```

### 6.3 Supporting modules

- **`dependencies.py`** — module-level singletons `DecisionPipeline(RealFeatureStore + 3 Stub* registries)` and `PipelineBridge`, imported by `canonical.py` and `ranking.py`: one `DecisionEngine`, one set of 9 models, one decision cache. Correct design, and the reason lazy loading paid off.
- **`engine.py`** — 9 canonical `.joblib` paths hardcoded and **duplicated** in two methods; lazy `_get_model_for_pair()`; forecast cache with `default=str`; `asyncio.new_event_loop()` per `policy_diff` fetch inside a thread pool (relevant to KNOWN_ISSUES A4).
- **`data/macro/`** — 23 provider modules; `service.get_historical_policy_rate` correctly refuses to backfill or simulate (documented invariant, and it holds). The defect is upstream in provider → series selection (§3.1).
- **Dead**: `layer1/data/forecast_data.py`, `layer1/decision/{decision_context,economic_filter,signal_validity}.py`.

### 6.4 Layer 3 — research layer

Unchanged for weeks; only `layer1/routers/model_comparison.py` couples it into the API.

| Area | Maturity |
| --- | --- |
| `evaluation/walk_forward.py` | ✅ `evaluate` / `evaluate_expanding` healthy |
| `evaluation/run_benchmarks.py` | ❌ `run_benchmarks.py:18` → `engine.xgb_model` AttributeError |
| `evaluation/model_evaluator.py` | ⚠️ random-fallback on predict failure |
| `experiments/run.py` | ❌ hardcoded metrics |
| `experiments/real_experiments.py` | ⚠️ unverified |
| `macro/regime.py` | ✅ |
| `models/arima.py` | ❌ `statsmodels` absent from `requirements.txt` **and** the environment |
| `models/{elastic_net,ensemble}.py` | ✅ |
| `rag/agents.py` | ⚠️ keyword scorer, not RAG |
| `research_gate/*` | ⚠️ `gate.py` works; `full_gate.py` passes `features={}` |
| `artifacts/registry.py` | ⚠️ schema incompatible with `backend/models/registry.json` |

The research corpus (`research_walkforward*.py`, `shadow_test*.py`, `research_validation_*`) is substantial and **unbound to anything served**. It is the cheapest available route to the validated metrics that F-03 says are missing.

### 6.5 Layer 4 — data quality

`PITValidator` (PIT-1…PIT-7) is correct and exercised by `backend/tests/test_pit_adversarial.py`; `config/policies.py` and `lineage/models.py` are implemented but **standalone** — no runtime forecast path validates PIT end-to-end (F-11), and `tests/pit_tests.py` is not discovered by pytest's default patterns (`*_tests.py`).

---

## 7. Frontend

Stack: React 18 · TS 5 · Vite 5 (5174) · Tailwind 3 · TanStack Query 5 · axios · date-fns · React Router 6 · Recharts 2. Brand: **Stratus Dynamics**. All UI strings English.

| Path | Page | Hooks → data |
| --- | --- | --- |
| `/` | GlobalPage | `useRanking`, `useActivePair`, `useForecastDashboard`, `useMarketIntelligence`, `useRegimeDivergence(pair,90,'1y')` |
| `/market` | MarketPage | `useRanking`, `useActivePair`, `usePrice(1y)`, `useForecastDashboard` |
| `/macro` | MacroPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair,5)` |
| `/risk` | RiskPage | `useRanking`, `useActivePair`, `useCanonicalRisk(pair,5)` |
| `/decision` | DecisionPage | `useRanking`, `useActivePair`, `useCanonicalDecision(pair,5)`, `useCanonicalNarrative` |
| `/about` | AboutPage | — |

12 hooks + `index.ts`; universe pinned to `FX_PAIRS` (9) in `constants/fxPairs.ts`; `types/contracts.ts` mirrors Layer 1 §7; `types/gaps.ts` G1–G5 must render `NOT_AVAILABLE`.

**Verification (2026-10-02):** `npm test` → **56 passed / 7 files** ✅ · `npm run build` → **PASS**, 1,501.61 kB / 305.81 kB gzip ✅ · `tsc --noEmit` ✅ (runs inside `build`).

**Caveats:** 4 hooks still raw-`fetch`, bypassing the axios client with its retry/backoff (F-18); `usePolling` orphaned; `forecast_eligibility` not in the decision contract so RESTRICTED renders as generic non-actionable (F-13); bundle grew +7 kB unminified this cycle because aggregation moved to the client (F-07); `VITE_API_URL` exists only in Cloudflare build env vars — no local fallback.

---

## 8. Deployment, verification & governance

| Target | What | Evidence / caveat |
| --- | --- | --- |
| **Render** (backend) | Docker service, `/health`, `uvicorn layer1.main:app`, PORT=10000 | `render.yaml`; ⚠️ no `ADMIN_TOKEN` (F-16) |
| **Cloud Run** | same image, `PORT` injected, `sh -c` expansion | ✅ supported since `d36c41b` |
| **Cloudflare Pages** (frontend) | static SPA, `VITE_API_URL` from Cloudflare env vars, `_headers`, `_redirects` | ✅ |
| **Vercel** (frontend) | Vite build → dist, SPA rewrites | legacy origin still in the CORS allowlist |
| **CI** | `ci.yml`: Python **3.11** compile + `pytest backend/layer4/tests/`; Node 20 build + test | 🔴 backend job collects 0 tests, **exit 5** (F-09). Also note CI pins 3.11 while the image is 3.12 |
| **Pre-commit** | hygiene + `pytest -q` always_run | enforced locally; this is currently the *only* automated backend gate |

**Governance.** Repo is prompt-first (`docs/Prompts/`) with contract-policing fidelity. Frozen specs: L1 **v5.1**, L2 **v3.4.1**, L3 **v5.0**, L4 **v3.1.1**. Ledgers: `STABLE.md` (current stable v2.7.5 @ `f45b097`), `KNOWN_ISSUES.md` (KI-001…KI-009, A3, A4, P1, B, Stub L4, Resolved), `README.md`.

**Governance lag is now the third-order problem.** The v2.7.x surfaces (regime gate, divergence surface, temporal contracts, risk-for-RESTRICTED, English intelligence, canonical ranking, CORS fix, lazy loading, cache fix) never went through traceability → gaps → freeze. And the ledger that should carry this cycle's blockers has no entry for them: **F-01, F-02, F-03, F-05, F-08 are not in `KNOWN_ISSUES.md`.** `informe.md` is where they currently live — untracked and truncated.

---

## 9. Status summary

**Green**
- 180/180 backend tests (20 files); frontend typecheck, build and 56/56 tests green.
- 9-pair canonical ranking with the KI-009 eligibility gate (6 ELIGIBLE / 3 RESTRICTED) and RiskEngine for all 9.
- Latency collapsed and holding: lazy model loading (~5 s startup vs ~3 min), cached `/ranking` < 100 ms.
- Forecast cache writes; CORS is a correct explicit allowlist; Docker is PORT-aware; frontend fully English under the Stratus Dynamics brand.
- Global page no longer contradicts the ranking surface.

**Amber**
- `/v1/status` self-reports `DEGRADED` with `model_drift CRITICAL` and 10% prediction coverage — the system knows it is degraded and still serves actionable signals.
- Registry split-brain, unconsumed `MERIDIAN_MODEL_DIR`, KI-002 residual, 3 Stub quality registries, Layer 3 tail broken, LLM half-wired, no `ADMIN_TOKEN` in Render.

**Red**
1. **F-01/F-02 — `policy_diff` is not `policy_rate`.** 5 of 9 currencies use long-term rates under a policy-rate label; 3 have no history; the one artifact that recorded it had zero variance. Nothing published about this feature's value survives this.
2. **F-03 — the promotion registry is mostly below random** (7/10 AUC < 0.5) and the survivor has no walk-forward validation attached.
3. **F-05 — horizon contract violation**: trained 10 d, served 5 d.
4. **F-08 — the economic layer is not economics**: a 63% 5-day expected return drives edge, actionability and position size.
5. **F-09 — CI collects 0 tests**; pre-commit is the only backend gate.
6. **F-07 — the previous cycle's "fix" moved business logic into the browser** and left a dead legacy endpoint publishing `total_pairs = 1`.

---

## 10. Corrections to previous reports, consolidated

See §2.1. Summary of the pattern: previous reports were strong on *engineering surface* (endpoints, tests, refactors) and silent on *evidentiary surface* (what the numbers mean). This cycle re-anchored the audit on the latter.

---

## 11. What we may and may not claim

| Claim | Status |
| --- | --- |
| "A traceable, explainable, contract-governed decision pipeline over 9 FX pairs, with an eligibility gate, risk engine and SHAP attribution" | ✅ **Supported** |
| "180 backend tests, 56 frontend tests, typecheck and production build pass" | ✅ **Supported** (re-measured 2026-10-02) |
| "Cold-start and ranking latency are production-viable" | ✅ **Supported** |
| "SHAP explains the decision" | ✅ **Supported** for the Logistic_24 pipeline (LinearExplainer fits, 61 samples) |
| "The macro differential feature carries predictive signal" | ❌ **Not supported** — semantically wrong for 5/9, absent for 3/9, constant in the one artifact that recorded it (F-01, F-02) |
| "The promoted models outperform a random baseline" | ❌ **Not supported** — 7/10 are below random; the 10th is unvalidated (F-03) |
| "A 63% expected 5-day return / `edge_ratio` 5.69 / position size $121,655" | ❌ **Not supported** — formula artefact, not a forecast (F-08) |
| "Fusion blends quant, macro and RAG signals (0.5/0.3/0.2)" | ❌ **Not supported** — macro and rag inputs are 0.0 (F-22) |
| "The 5-day decision is a 5-day model output" | ❌ **Contradicted** — trained at 10 d (F-05) |
| "Data quality is *good*" on the Decision page | ⚠️ **Constant** — comes from a `StubDataQualityRegistry(0.90)` (F-12) |
| "Meridian currently covers 9 pairs" | ⚠️ **True on 3 surfaces, false on 1** — `/v1/market-intelligence` says 1 (F-07) |

---

## 12. Recommendations

### Wave 0 — credibility blockers (do before any external claim; est. 2–4 days)

1. **Freeze external performance claims.** Until items 2–5 land, the only defensible public statement is the product-capability one from §11.
2. **Decide `policy_diff`'s fate — re-source or remove.** Cheapest correct path: switch CHF → `SNBPolicyRateProvider` and MXN → `BanxicoProvider` (both already implemented and unused for this), add BoE/BoJ/BCB official sources, and for CNY/ARS/BOB make `policy_diff` explicitly **`unavailable`** rather than imputed. Then **retrain**. Alternative: drop the feature from `feature_cols` and retrain at the correct horizon — one decision, one script change, and the semantic debt disappears with it.
3. **Attach provenance to artifacts.** Every `.joblib` must carry `training_period`, `feature_provenance` (per-feature source series + semantic label), `horizon`, and a validation metric. Today 4 of 9 serving models carry none of this.
4. **Bind validated metrics to promoted models.** Re-run the existing `research_walkforward*.py` corpus over the 9 canonical models, or mark them `unvalidated` in the registry. Four registry entries with round metrics (0.45/0.43/0.42/0.44) should be re-derived or deleted.
5. **Fix the horizon contract** (F-05): either serve `horizon_days = 10`, or retrain at 5. Do not ship the mismatch either way.

### Wave 1 — consistency and verification (est. 1 week)

6. **Fix CI** (F-09): run `pytest` from the repo root against `pytest.ini`, install `backend/requirements.txt`, rename `pit_tests.py` → `test_pit_layer4.py`, align the CI Python version with the image (3.12).
7. **One registry** (F-04): pick the root `models/registry.json` as authoritative, repoint `engine.py`, delete `backend/models/registry.json` and the `.backup_20260914` file. `/v1/status` should then stop reporting 10% coverage.
8. **Unify intelligence on the server** (F-07): port the `+302`-line adapter from `useMarketIntelligence.ts` back into `routers/intelligence.py` on top of the `PipelineBridge`, retire the legacy `RankingEngine` (or delete it), and have the frontend go back to a single transport call. Business logic belongs in one place and under one contract.
9. **Label honestly** (F-06): make `artifact.model_id`/`model_version` reflect `Logistic_24` + artifact hash; add a `validated: bool` field.
10. **Add `ADMIN_TOKEN` to `render.yaml`** (F-16) or delete the regenerate endpoint.
11. **Re-attach the branch** (F-17) and commit this cycle's docs.

### Wave 2 — architecture debt (v2.8 → v3.0)

12. **Real quality registries** (F-12): back `DataQuality`/`Freshness`/`Drift` with `PITValidator`; remove the `⚠ STUB` badge by making the numbers real.
13. **Close KI-002 properly** (F-11): drop the wall-clock `as_of` fallback, populate real `input_available_times`, capture VIX timestamps, then close A/B/C.
14. **Make the economic layer economic** (F-08): replace the volatility-rescaled `expected_return` with either a calibrated return model or an explicit, documented uncertainty band; recompute `edge_ratio`/`position_size` from it; and stop presenting a probability-derived number as a return.
15. **Fix or delete the Layer 3 tail** (F-14): port `run_benchmarks.py` to `_get_model_for_pair` or delete it; decide on `statsmodels`; replace `experiments/run.py` metrics.
16. **Reconcile the two macro paths** (F-20) and make the fusion weights honest (F-22): either feed macro/RAG or drop them from the declared weights.
17. **Frontend**: surface `forecast_eligibility` (F-13); move the 4 raw-`fetch` hooks onto `apiClient`; delete `usePolling`; enable minification + route-level code splitting (1.50 MB → target < 700 kB).
18. **Governance catch-up** (F-19): register F-01/F-02/F-03/F-05/F-08 in `KNOWN_ISSUES.md` with owners; correct item **B** (fixed by `57566db`, superseded by `da77805`); bump `STABLE.md` to a v2.8 checkpoint; fix the `README.md` header (v2.7.5, English); finish or delete the truncated `informe.md`.

---

## 13. Reproduction

```bash
# verification gates
python3 -m pytest -q                                    # 180 passed
python3 -m pytest backend/layer4/tests/ ; echo $?       # exit 5 — 0 collected (CI's exact command)
cd frontend && npm test && npm run build                # 56 passed; 1,501.61 kB

# registry split-brain (F-04)
python3 -c "import json;[print(p,[(m['model_id'],m['active'],m['metrics']['auc']) for m in json.load(open(p))['models']]) \
  for p in ('backend/models/registry.json','models/registry.json')]"

# artifact provenance + horizon (F-02, F-05)
python3 -c "import joblib,glob;[print(f, (o:=joblib.load(f))['horizon'], o.get('training_period'), o.get('policy_diff_stats')) \
  for f in sorted(glob.glob('models/canonical/*.joblib'))]"

# live surface (needs no server)
python3 -c "from fastapi.testclient import TestClient;from backend.layer1.main import app;c=TestClient(app);\
print(c.get('/v1/fx/ranking').json()['total_pairs'], c.get('/v1/market-intelligence').json()['source'])"

# grep-level checks
grep -rn "IRLTLT01\|INTDSRBRM" backend/layer2/data/macro/providers/   # F-01
grep -rn "MERIDIAN_MODEL_DIR" --include=*.py backend                 # F-10 (no output)
```

---

*Regenerate this document together with `architecture.md` on every cycle that changes a served surface, a model artifact, or a verification result. Findings IDs (F-nn) are stable and should be cross-referenced from `KNOWN_ISSUES.md`.*
