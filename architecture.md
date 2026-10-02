# Meridian FX — Architecture

> Last reviewed: **2026-10-02** · HEAD `27746d2` (detached, == `origin/main`) · 231 commits · latest tag `v2.7.5` (`f45b097`), 37 commits behind · 13 FastAPI routers
> Verification 2026-10-02: backend **180 passed / 20 files** · frontend **56 passed / 7 files** + typecheck PASS + build PASS (**1,501.61 kB / 305.81 kB gzip**) · CI backend job **0 tests collected (exit 5)**
> Prior revision: 2026-09-16 (HEAD `f78af89`)

This document describes the architecture **as implemented**, and — new in this revision — §13 states the target architecture with the concrete deltas required to reach it. Where implementation and contract disagree, the disagreement is called out inline and cross-referenced to `report.md` findings (**F-nn**).

---

## 1. System context

Meridian FX is a four-layer forecasting platform for FX pairs. Request flow is strictly downward (Layer 1 → Layer 2 → Layer 3 → Layer 4); no layer depends on a layer above it. Research artefacts (`models/`) produced in Layer 3 feed the live engine in Layer 2 via a versioned registry gated by a quality contract.

```
Browser (React/Vite SPA, 6 routes)
   │
   ▼
[Layer 1] FastAPI delivery API — 13 routers, DTO/aggregation
   │  (dependencies.py PipelineBridge singleton, decision_engine_adapter, pair_normalizer)
   ▼
[Layer 2] Live engine — lazy Logistic_24 loader + XGBoost/registry, SHAP, data providers
   │  (yahoo/twelve/alpha_vantage/fred + data/macro 23 providers), pipeline_bridge,
   │  ranking engine (legacy, intelligence-only), status, SQLite narrative, pit_adapter
   ▼
[Layer 3] Research layer — walk_forward, gate.py + experiments E0–E7 (standalone)
   │
   ▼
[Layer 4] Data-quality layer (PIT) — PITValidator PIT-1…PIT-7, config policies, lineage, pit_tests.py
```

### 1.1 Key relationships (pairs `a:b`)

- **`ranking:canonical`** — `/v1/fx/ranking` evaluates the 9-pair canonical universe through the **same `PipelineBridge`** as `/v1/canonical/{pair}/decision`: one `DecisionEngine`, one set of 9 Logistic_24 models, one decision cache. `LONG/SHORT/NEUTRAL → UP/DOWN/NEUTRAL` at the legacy contract boundary.
- **`intelligence:frontend`** *(new, `da77805`)* — the Global page's intelligence aggregate is now **assembled in the browser** from `/v1/fx/ranking`. The server-side `/v1/market-intelligence` still runs the legacy `RankingEngine` and is **no longer called by the client**. Consequence: aggregation logic exists in two languages, and the server publishes a surface (`total_pairs = 1`) that contradicts the canonical one (**F-07**). Target: move the adapter back to Layer 1 (§13.1).
- **`decision-engine:regime`** — starts from exchange regime (KI-009), then `DataQualityRegistry` → KnowledgeBase (KI-002) → context → engine → per-decision gate policy.
- **`regime:engine`** — `RiskEngine` is computed for RESTRICTED decisions (Opción B); the verdict (OPEN/RESTRICTED) changes the requirement to *return a signal*, never the requirement to *run the engine*.
- **`regime:frontend`** — `RegimeWarningBanner` reads `engine.regime`; `DivergencePanel` reads `/v1/fx/{pair}/regime-divergence`.
- **`features:macro`** *(defect, F-01)* — the canonical 24-feature vector is 23 technical + `policy_diff`, sourced from `data/macro` providers. The PIT alignment is sound; the **semantics of the input series are not** for 5 of 9 currencies, and absent for 3.

### 1.2 The three architectural inconsistencies that shape everything else

| # | Inconsistency | Where | Effect |
| --- | --- | --- | --- |
| 1 | **Two registries, two truths about "active"** | `backend/models/registry.json` (10 active) vs `models/registry.json` (1 active) | `/v1/status` = DEGRADED, `prediction_coverage 0.1`; legacy ranking = 1 pair (F-04) |
| 2 | **Two macro paths for one pair** | `MacroService.get_historical_policy_rate` (engine) vs `macro_data_status` (decision DTO) | Same request reports `quote_rate: null` *and* a computed `policy_diff` (F-20) |
| 3 | **Two horizon contracts** | `HORIZON = 10` (training) vs `horizon_days = 5` (bridge, DTO, UI) | The served label contradicts the trained target (F-05) |

---

## 2. Repo map (top-level)

| Blob | Purpose |
|---|---|
| `backend/layer1/` | Delivery API: 13 routers, `dependencies.py`, 2 adapters, `llm/`, `models/responses.py`, `utils/pair_normalizer.py`. |
| `backend/layer2/` | Live engine: `engine.py` (lazy Logistic_24, `policy_diff`), `pipeline_bridge.py`, `data/` (4 market sources + `data/macro/` 23 providers), `features/`, `explainers/shap_explainer.py`, `models/`, `narrative/`, `status/`, `quality/pit_adapter.py`, `ranking/` (legacy). |
| `backend/layer3/` | Research: `artifacts/`, `evaluation/`, `experiments/`, `macro/regime.py`, `models/`, `rag/`, `research_gate/`. |
| `backend/layer4/` | Data quality: `quality/pit_validator.py`, `config/policies.py`, `lineage/models.py`, `tests/pit_tests.py`. |
| `backend/src/meridian_fx/` | Contract-governed engine package: `contracts/`, decision + risk engine, `divergence/`, gates, quality, `Stub*` registries, sizing, validation. |
| `backend/models/` | 10 `.pkl` artifacts + `registry.json` (10 entries, **all active**). |
| `frontend/` | React/Vite SPA: 6 pages, 12 hooks + `index.ts`, components, `services/api.ts`, `types/contracts.ts`. |
| `docs/` | Frozen specs (L1 v5.1, L2 v3.4.1, L3 v5.0, L4 v3.1.1) + governance + `divergence/README.md`. |
| `models/` | `canonical/` (10 Logistic_24 `.joblib` + 2 metadata JSON), `experimental/`, `registry.json` (10 entries, **1 active: USD/CHF**) + `registry.json.backup_20260914_140136`. |
| `Dockerfile` | `python:3.12-slim`; `COPY models/ backend/`; `PYTHONPATH=/app/backend:/app`; `MERIDIAN_MODEL_DIR=/app/models` (**no consumer**, F-10); `EXPOSE 8080`; PORT-aware CMD. |
| `render.yaml` · `runtime.txt` | Render Docker service, `/health`, PORT=10000; FRED/GROQ/AV/TWELVE keys — **no `ADMIN_TOKEN`** (F-16). |
| `pytest.ini` | `testpaths = backend/tests`, `pythonpath = ., backend, backend/src`, `asyncio_mode = auto`. |
| `.github/workflows/ci.yml` · `.pre-commit-config.yaml` | CI (backend job **collects 0 tests**, exit 5) + pre-commit (hygiene + `pytest -q`, `always_run`). |
| `STABLE.md` · `KNOWN_ISSUES.md` · `README.md` | Governance. STABLE = v2.7.5 @ `f45b097`; README header stale (F-19). |
| `scripts/` | `audit_consistency.py`, `audit_registry.py`, `apply_gate.py`. |
| Research scripts (root) | `research_gate.py`, `research_walkforward*.py` (7 result files), `research_validation_*`, `shadow_test*.py`, `train_*`, `monitor_*`, `evaluate_all_pairs.py`, `final_holdout.py`. |
| `informe.md` · `comandos.md` | ⚠ untracked; `informe.md` is the macro audit (truncated at line 445). |

---

## 3. Layer 1 — FastAPI delivery API (`backend/layer1/`)

### 3.1 Routers (13)

| Router | Endpoint(s) |
|---|---|
| `canonical.py` | `GET /v1/canonical/{pair}/decision` · `GET /v1/canonical/{pair}/risk` |
| `narrative.py` | `GET /v1/canonical/{pair}/narrative` · `POST /v1/canonical/{pair}/narrative/regenerate` |
| `ranking.py` | `GET /v1/fx/ranking` — **canonical 9-pair** (PipelineBridge, `asyncio.gather`) |
| `forecast.py` | `GET /v1/fx/{base}/{quote}/forecast` |
| `performance.py` | `GET /v1/fx/performance/{pair}?period=` |
| `status.py` | `GET /v1/status` |
| `intelligence.py` | `GET /v1/market-intelligence` — ⚠ **legacy `RankingEngine`**, `total_pairs = 1`, now unconsumed (F-07) |
| `historical.py` | `GET /v1/fx/{pair}/historical` — random-synthetic fallback |
| `interpretation.py` | `GET /v1/fx/interpretation?pair=&include_macro=` — macro hardcoded |
| `price.py` | `GET /v1/fx/{pair}/price?period=` |
| `model_comparison.py` | `GET /v1/fx/{pair}/model-comparison` — Layer 3 `evaluate_expanding` |
| `forecast_dashboard.py` | `GET /v1/fx/{pair}/forecast-dashboard` — `model.version = "v1.0"` ≠ `Logistic_24` (P1) |
| `divergence.py` | `GET /v1/fx/{pair}/regime-divergence?window_days=&period=` |

Plus `/` and `/health`. No `/drivers`.

### 3.2 Supporting modules

- **`main.py`** — app factory; CORS as an **explicit allowlist** (no wildcard + credentials, since `f78af89`): localhost 5173/5174, 127.0.0.1, Cloudflare Pages `*.pages.dev`, legacy Vercel, ngrok. 13 `include_router` calls.
- **`dependencies.py`** — module-level singletons `DecisionPipeline(RealFeatureStore + 3 Stub* registries)` and `PipelineBridge`. Imported by `canonical.py` and `ranking.py` so both surfaces share one `DecisionEngine`, one model set and one decision cache. This is the correct seam and the reason lazy loading worked.
- **`routers/ranking.py`** — `57566db`: `CANONICAL_FX_PAIRS` (9), `_evaluate_pair_for_ranking` via `bridge.evaluate_pair(pair, horizon_days=5)`, direction map, RESTRICTED pairs included with `actionable=False, confidence=0.0`, legacy `opportunity_score` formula preserved. Measured: `total_pairs=9`, 4 actionable.
- **`routers/intelligence.py`** — `from backend.layer2.ranking.engine import RankingEngine` (line 16), instance at 22, used at 429, and self-reported at 464. ⚠ The last server-side consumer of the legacy engine.
- **`routers/divergence.py`** — `DataProvider().get_historical` + `get_exchange_regime` + `compute_divergence_report`; serializes observed/projected/divergence series, z-score, interpretation, `last_date`.
- **`adapters/decision_engine_adapter.py`** — derives `as_of` from `forecast['data_provider']['last_date']`; wall-clock fallback logged (KI-002-A).
- **`adapters/decision_to_response.py`** — decision DTO assembly. Emits `model_id`/`model_version` that do not identify the running model (F-06).
- **`llm/`** — `LLMFallbackManager` reachable via narrative only; `EconomicInterpreter` unimported (F-15).
- **Dead** — `data/forecast_data.py`, `decision/{decision_context,economic_filter,signal_validity}.py`.

---

## 4. Layer 2 — live engine (`backend/layer2/`)

### 4.1 Forecast path (canonical, per pair)

```
Yahoo → Twelve → Alpha Vantage → FRED        (market data; last_date = cutoff)
   ↓
features: technical (23) + derived + macro
   ↓
MacroService.get_historical_policy_rate(base, quote)
   └─ provider → series → calculate_historical → merge_asof(backward) → policy_diff
   ↓
Logistic_24 (lazy per pair) — Pipeline(imputer=median, StandardScaler, LogisticRegression(balanced))
   ↓
DecisionEngine.get_forecast  → + data_provider.last_date
   ↓
SHAP LinearExplainer (quant attribution)  →  canonical Decision DTO
```

**Contract boundaries that are currently violated:**

| Boundary | Contract | Actual | Finding |
| --- | --- | --- | --- |
| provider → feature | `policy_diff` = policy-rate differential | long-term rates for GBP/JPY/CHF/MXN/BRL; empty for CNY/ARS/BOB | **F-01** |
| trainer → artifact | feature provenance + horizon | 4 artifacts carry no `training_period`; `policy_diff` constant in the extended model | **F-02** |
| trainer → bridge | `horizon` | 10 vs 5 | **F-05** |
| engine → economic layer | `expected_return` | `(2p−1)·vol·√(h/365)` — a probability rescaling, not a return | **F-08** |

### 4.2 Module responsibilities

| File | Responsibility |
|---|---|
| `engine.py` | Forecast orchestration (Logistic_24 → heuristic). 9 canonical paths **hardcoded and duplicated** (51–59 / 159–167); lazy `_get_model_for_pair()` (`4af2a45`); forecast cache with `default=str` (`2f24fe1`); `_load_canonical_model()` kept as a no-op; unreachable dead code at 122–127 (F-21). Reads `backend/models/registry.json`. |
| `pipeline_bridge.py` | Per-minute decision cache; `evaluate_pair(pair, horizon_days=5)`; emits `_cache {hit, bucket}`. |
| `ranking/engine.py` | **Legacy** XGBoost/registry ranking; alive for `intelligence.py` only. |
| `data/` | `provider.py`, `fetcher.py`, `validator.py`, sources `yahoo/twelve/alpha_vantage/fred`, `macro/` (23 provider modules + `differential_provider.py`, `service.py`, `differential_status.py`). |
| `features/` | `technical.py` (23 features), `derived.py`, `macro.py`. |
| `explainers/shap_explainer.py` | SHAP economic breakdown (LinearExplainer, 61 samples). |
| `models/` | `registry.py`, `registry_adapter.py`, `model_selector.py`, `logistic_model.py`, `xgboost_model.py`, `trainer.py`. |
| `narrative/` | `generator.py`, `prompt_builder.py`, `repository.py` (SQLite), `service.py` — cache-first, **no TTL**, keyed `(pair, horizon, narrative_key, prompt_version)`. |
| `status/engine.py` | `/v1/status`; reads root `models/registry.json`. |
| `quality/pit_adapter.py` | PIT adapter. |

### 4.3 Model resolution and the registry split-brain

| Consumer | Registry read | Active set |
|---|---|---|
| `layer2/engine.py:24` | `backend/models/registry.json` | **10 / 10 active** |
| `layer2/models/registry.py`, `layer2/status/engine.py` (defaults) | `models/registry.json` (root) | **1 / 10 active** (USD/CHF) |
| Frontend `/v1/performance` | via status | 1 |

`models/` also holds `registry.json.backup_20260914_140136`. The two files are **not** byte-identical. Measured consequence: `/v1/status` → `DEGRADED`, `model_drift CRITICAL`, `prediction_coverage 0.1`, and the legacy ranking returning one pair (**F-04**).

Canonical artefacts live in `models/canonical/*.joblib`, resolved **CWD-relative** (works in Docker because `WORKDIR /app`); `MERIDIAN_MODEL_DIR` has **zero** consumers (F-10).

Artifact shape (all 10): `Pipeline(imputer, scaler, LogisticRegression(balanced, max_iter=1000, random_state=42))`, 24 features including `policy_diff`, `horizon: 10`. 5 record `training_period` (830 samples, 2023-06-15 → 2026-08-26); the extended EUR/USD artifact records 1092 samples (2022-06-14 → 2026-08-26) and the constant `policy_diff_stats` of §3.2 of the report.

### 4.4 Exchange-regime classification (KI-009)

`contracts/exchange_regime.py`:

| Pair | Regime | Verdict |
|---|---|---|
| USD/JPY, EUR/USD, GBP/USD, USD/CHF, USD/MXN, USD/BRL | FREE_FLOAT | OPEN |
| USD/CNY | MANAGED_FLOAT | RESTRICTED |
| USD/ARS, USD/BOB | UNKNOWN | RESTRICTED |

Provisional (BCB/BCRA primary-source verification pending). RESTRICTED → signal `UNAVAILABLE`, `actionable=False`, `forecast_eligibility` preserved, **RiskEngine still computed** (Opción B).

---

## 5. Layer 3 — research layer (`backend/layer3/`)

- `artifacts/registry.py` — research checkpoint registry; **schema incompatible** with `backend/models/registry.json`.
- `evaluation/` — `walk_forward.py` (`evaluate`, `evaluate_expanding`) ✅; `model_evaluator.py` ⚠️ (random fallback on predict failure); `run_benchmarks.py` ❌ (`engine.xgb_model` AttributeError, line 18); `benchmarks.py`, `decision_policy.py`.
- `experiments/` — `run.py` ❌ hardcoded metrics; `real_experiments.py` ⚠️ unverified.
- `macro/regime.py` — `MacroRegimeEngine` ✅.
- `models/` — `arima.py` ❌ (`statsmodels` absent from `requirements.txt` **and** the environment; the divergence module deliberately avoids it); `elastic_net.py`, `ensemble.py` ✅.
- `rag/agents.py` — `CentralBankSentimentEngine`: keyword scorer, not RAG. Feeds `rag_score`, which is hardcoded `0.0` at runtime (F-22).
- `research_gate/` — `gate.py` ✅, `real_gate`, `full_gate` ⚠️ (passes `features={}`).

Only `layer1/routers/model_comparison.py` couples Layer 3 into the API. The walk-forward corpus at the repo root is **substantial and unbound to any served model** — it is the cheapest source of the validated metrics F-03 requires.

---

## 6. Layer 4 — data-quality layer (`backend/layer4/`)

- `quality/pit_validator.py` — `PITValidator` (PIT-1…PIT-7) ✅ correct; exercised by `backend/tests/test_pit_adversarial.py` and the temporal/`as_of` tests.
- `config/policies.py`, `lineage/models.py` — implemented but **standalone**: no runtime forecast path validates PIT end-to-end.
- `tests/pit_tests.py` — compiles; **not discovered** (default patterns are `test_*.py` / `*_test.py`).

Positive: `FeatureValue` carries a real `TemporalProvenance` chain, and the adapter derives `as_of` from the market-data cutoff rather than wall clock when data is present.

---

## 7. Contract-governed Decision Engine (`backend/src/meridian_fx/decision/`)

Entry `pipeline.py`, frozen against `docs/Product_specification/Layer_02.md` v3.4.1. Backed by 180 tests.

```
DecisionPipeline (via PipelineBridge.evaluate_pair)
  ├─ step 0 (KI-009) exchange-regime eligibility gate  ── RESTRICTED short-circuit (no scoring; Risk still computed)
  ├─ step 1 (KI-002) TemporalProvenance._arg_filter    ── as_of from L4 data_provider.last_date
  ├─ step 2 (KI-002) context loading (registry)        ── DataQualityRegistry (capability)
  ├─ step 3 (KI-006) capability checks                  ── explicit types
  ├─ step 4          conditions (+ args) store
  └─ shipped: one topline model; decision list; data inputs; verdict
```

Runtime semantics: **all contracts are runtime-free** — nothing is computed at decision time.

### 7.1 Temporal contracts

`contracts/temporal.py`: `TemporalProvenance` + `TemporalConfidence` (KI-002-D; PIT-7 ordering enforced). `FeatureValue` carries provenance. Residual gaps: wall-clock `as_of` fallback, `input_available_times = [as_of]` making PIT-2 vacuously true, synthetic VIX timestamps (F-11).

### 7.2 Regime-divergence module

`divergence/{arima,metrics,report}.py` — scipy `minimize`-fit ARIMA(1,0,1) on log-returns, 90-observation rolling window, one-step-ahead projection, rolling z-score, thresholds `normal / notable / extreme / persistent`. Endpoint `GET /v1/fx/{pair}/regime-divergence`; docs `docs/divergence/README.md`; frontend `useRegimeDivergence.ts`, `DivergencePanel.tsx`, `RegimeWarningBanner.tsx`.

### 7.3 Stub L4 registries

The pipeline is initialised with `StubDataQualityRegistry(0.90)`, `StubFreshnessRegistry(3.0)`, `StubDriftRegistry(0.05)` in `layer1/dependencies.py`. They return constants and are surfaced in the UI with a `⚠ STUB` badge — the Decision page's "data quality: good" is a literal (F-12).

---

## 8. Frontend — contract-driven dashboard (`frontend/`, English, Stratus Dynamics)

### 8.1 Routes & hooks

Routes: `/` GlobalPage, `/market` MarketPage, `/macro` MacroPage, `/risk` RiskPage, `/decision` DecisionPage, `/about` AboutPage.

Hooks (12 + `index.ts`): `useActivePair`, `useCanonicalDecision`, `useCanonicalNarrative`, `useCanonicalRisk`, `useForecast`, `useForecastDashboard`, `useMarketIntelligence`, `usePerformancePeriod`, `usePolling` (orphaned), `usePrice`, `useRanking`, `useRegimeDivergence`.

Universe pinned to `FX_PAIRS` (9) in `constants/fxPairs.ts`. Transport: `services/api.ts` (axios, timeout, exponential backoff) + `services/{forecast,ranking,performance,status}.ts`. Domain contracts declared inside hooks; `types/contracts.ts` mirrors Layer 1 §7; `types/gaps.ts` G1–G5 must render `NOT_AVAILABLE`.

**Architectural exception (new, `da77805`):** `useMarketIntelligence.ts` (+302 lines) no longer calls `/v1/market-intelligence`; it adapts `GET /v1/fx/ranking` into the `MarketIntelligence` shape **in the client** — including `current_context`, `decision_view`, `key_signals` and `summary` text. This is presentation-adjacent aggregation, not transport, and it is now the second implementation of the same business rules (F-07). Four hooks (`usePrice`, `useRanking`, `useMarketIntelligence`, `useForecastDashboard`) still use raw `fetch` and therefore bypass the axios client's retry/backoff (F-18).

### 8.2 Presentational components

`components/global/` — `RegimeWarningBanner`, `DivergencePanel`, `ActionableInfo`, `IntelligenceBrief`, `LeadingSignals`, `MarketIntelligenceHero`, `ModelExplanation`, `PriceChartSignalIQ`, `RankingTable`. `components/decision/` — `DecisionHero/Metrics/Narrative/Provenance/ShapPanel/Validity`, `EconomicBreakdown`, `HardGates`, `QualityMetrics`, `SignalFusion`. `common/` — `ApiError`, `ErrorBoundary`, `LoadingSpinner`, `RegimeBar`, `StatusBadge`, `ThemeProvider`, `UniverseSelector`. `layout/` — `Header`, `Footer`, `MainLayout`. Plus `market/`, `macro/`, `risk/`, `forecast/`.

### 8.3 Layering rules

Frontend is **request/response** (no store). Container components import hooks; leaf components never do. `import type` is strict. Contract gaps render as `NOT_AVAILABLE` — no fallback derivation. `forecast_eligibility` is **not** in the decision contract, so RESTRICTED and INSUFFICIENT_EDGE are indistinguishable in the UI (F-13).

---

## 9. Deployment & runtime

- **`Dockerfile`** — `python:3.12-slim`, `WORKDIR /app`, installs `backend/requirements.txt`, `COPY models/ backend/`, `ENV PYTHONPATH=/app/backend:/app MERIDIAN_MODEL_DIR=/app/models`, `EXPOSE 8080`, `CMD sh -c "uvicorn layer1.main:app --host 0.0.0.0 --port ${PORT:-8080}"`.
- **`render.yaml`** — Render Docker web service (free), `healthCheckPath /health`, PORT via Render (10000). Declares FRED/GROQ/ALPHA_VANTAGE/TWELVE_DATA but **not `ADMIN_TOKEN`**, so `POST /v1/canonical/{pair}/narrative/regenerate` returns 503 in production (F-16).
- **Cloud Run** — same image; `PORT` injected (default 8080) since `d36c41b`.
- **Cloudflare Pages / Vercel** — static SPA; `VITE_API_URL` from **Cloudflare build env vars** (repo `.env*` untracked since `1d14c89`); SPA rewrites + `_headers`/`_redirects`.
- **CORS** — explicit allowlist + credentials; no wildcard.
- **CI** (`.github/workflows/ci.yml`) — backend job: Python **3.11** `compileall backend` + `pytest backend/layer4/tests/` (**0 collected, exit 5**; also 3.11 vs the image's 3.12). Frontend job: Node 20 `npm ci` + `npm run build` (includes `tsc --noEmit`) + `npm test`. Pre-commit: hygiene + `pytest -q` (`always_run`) — currently the **only** automated backend gate.
- **Local orchestration** — `backend/docker-compose.yml` (ports 10000:10000, env keys, mounts `models/` + `cache/`); `start.sh` / `stop.sh`.

---

## 10. Documentation & governance

`README.md` (header still "v2.7 … tag `v2.7` pendiente", partially Spanish), `STABLE.md` (current stable **v2.7.5 @ `f45b097`** — 37 commits behind HEAD), `KNOWN_ISSUES.md` (KI-001…KI-009, A3 `policy_diff` PIT audit, A4 async audit, P1 model-version mismatch, B legacy-vs-canonical ranking, Stub L4, Resolved), `docs/divergence/README.md`. Tags: `v2.7`, `v2.7.1`–`v2.7.5`.

**Governance gaps.** Item **B** is stale: it reads "deferred to v3.0" although `57566db` fixed the endpoint and `da77805` moved the consumer client-side. More importantly, the credibility blockers of this cycle — F-01, F-02, F-03, F-05, F-08 — **have no entry in `KNOWN_ISSUES.md`**; they currently live only in the untracked, truncated `informe.md` (F-19).

---

## 11. Verification matrix (2026-10-02)

| Area | Command | Result |
|---|---|---|
| Backend tests | `python3 -m pytest -q` (root `pytest.ini`) | ✅ **180 passed / 20 files** (31.5 s) |
| CI backend job | `python3 -m pytest backend/layer4/tests/` | 🔴 **exit 5, 0 collected** |
| Frontend tests | `npm test` (TZ=UTC vitest run) | ✅ **56 passed / 7 files** (2.7 s) |
| Typecheck | `tsc --noEmit` (inside `npm run build`) | ✅ PASS |
| Production build | `npm run build` | ✅ PASS — 1,501.61 kB / **305.81 kB gzip** |
| Live `/health` | TestClient | ✅ `{"status":"healthy"}` |
| Live `/v1/status` | TestClient | ⚠️ `DEGRADED`, `model_drift CRITICAL`, `prediction_coverage 0.1` |
| Live `/v1/fx/ranking` | TestClient | ✅ `total_pairs = 9`, **4 actionable** |
| Live `/v1/market-intelligence` | TestClient | 🔴 `source.total_pairs = 1`, `total_actionable = 0` |
| Live decision USD/CHF | TestClient | ✅ 200, SHORT, conf 0.641, `net_return 56.93`, `macro_data_status PARTIAL` |
| Live decision USD/ARS | TestClient | ✅ 200, RESTRICTED (`actionable=false`, `gate=null`, risk 65.6 HIGH) |
| Startup / cold path | lazy model loading | ✅ ~5 s startup; cached `/ranking` < 100 ms |
| CORS | config inspection | ✅ explicit allowlist, no wildcard (`f78af89`) |

---

## 12. Architectural risks

Ordered by blast radius, not by discovery date.

1. **Feature semantics are not contractual.** Nothing in the pipeline verifies that a macro input means what its name says; `policy_diff` has silently meant "long-term rate differential" for 5 of 9 currencies. There is no artifact-level provenance manifest to catch it. (F-01, F-02)
2. **Two registries, two definitions of "active".** The engine and the status/registry layer disagree; the API therefore advertises 10% coverage while serving from a 10-model set, and the legacy surface advertises 1 pair. (F-04)
3. **The economic layer is a rescaling, not a model.** `expected_return → edge_ratio → position_size → actionability` all derive from `(2p−1)·vol·√(h/365)`. The decision to act is therefore a function of model confidence and volatility scaling, not of an expected monetary outcome. (F-08)
4. **The horizon contract is broken end to end.** Training, bridge, DTO and UI disagree (10 vs 5). (F-05)
5. **Verification does not cover the system.** CI collects 0 backend tests; the 180-test suite runs only via pre-commit. Nothing prevents a regression from merging. (F-09)
6. **Aggregation logic has migrated into the client.** ~300 lines of ranking→intelligence business rules now live in TypeScript while the server keeps a contradictory endpoint alive. Two implementations, one contract, no owner. (F-07)
7. **Declared multi-signal fusion is single-signal.** Macro and RAG inputs are `0.0`; weights 0.3/0.2 are decorative. (F-22)
8. **Quality gating is a constant.** Three `Stub*` registries feed the visible "data quality" and drift scores. (F-12)
9. **PIT is scaffolding, not enforcement.** Provenance exists on the types but no runtime path validates it; PIT-2 is vacuously satisfied. (F-11)
10. **Artifact metadata cannot identify the model.** `artifact.model_id = "logistic_USD_CHF"`, `model_version = "logistic-v1.0"` while `Logistic_24` runs; no validation metric is attached to any promoted artifact. (F-06, F-03)
11. **Research output is disconnected from production.** Walk-forward, shadow and holdout results exist for nothing that is served. (F-03, F-14)

---

## 13. Target architecture

The delta between §1–§12 and a defensible v2.8/v3.0. Each item names the finding it closes.

### 13.1 One intelligence surface, computed on the server

Move the `useMarketIntelligence` adapter back into `routers/intelligence.py`, built on the shared `PipelineBridge`, and retire `layer2/ranking/engine.py`. The frontend returns to a single transport call; the `/v1/fx/ranking` vs `/v1/market-intelligence` contradiction disappears by construction. **Closes F-07.**

### 13.2 One registry, one model-resolution point

Root `models/registry.json` becomes authoritative; `backend/models/registry.json` and the `backup_20260914` file are deleted; `engine.py`, `status/engine.py` and `models/registry.py` all resolve through one helper that honours `MERIDIAN_MODEL_DIR` with a CWD fallback. The duplicated 9-path literal collapses into that helper. **Closes F-04, F-10.**

### 13.3 A feature-provenance contract

Introduce `FeatureProvenance {name, source, series_id, semantic_label, available_from, quality}` and require it (a) in the training pipeline, (b) inside every `.joblib` artifact, (c) in the `PredictionArtifact` DTO. A provider that cannot supply a defensible `semantic_label` for `policy_rate` must publish `policy_diff` as **unavailable**, and the pipeline must degrade explicitly rather than through `SimpleImputer(median)`. Official providers already in the tree (`SNBPolicyRateProvider`, `BanxicoProvider`) become the defaults for CHF and MXN; BoE/BoJ/BCB sources are added; CNY/ARS/BOB stay unavailable until a primary source exists. **Closes F-01, F-02, F-20.**

### 13.4 A single horizon contract

`horizon` becomes a first-class field of the model artifact, propagated unchanged to `PredictionArtifact`, the bridge cache key, the API DTO and the UI. Retrain at the served horizon (or serve 10) so the two cannot diverge. **Closes F-05.**

### 13.5 An economic layer that means something

Replace the volatility-rescaled `expected_return` with either (a) a calibrated return model trained on realised forward returns, or (b) an explicit probability + calibrated uncertainty band, with `edge_ratio` and `position_size` derived from the band and from cost estimates (`costs` already exists in the DTO). Until then, the UI must not present these fields as expected returns. **Closes F-08.**

### 13.6 Real quality gating

`StubDataQualityRegistry` / `StubFreshnessRegistry` / `StubDriftRegistry` are replaced by `PITValidator`-backed implementations reading the same provenance chain as §13.3; the `⚠ STUB` badge disappears because the numbers become real. **Closes F-12, and contributes to F-11** by making PIT enforcement a runtime path rather than a test-only one.

### 13.7 Verification that actually gates

CI runs `pytest` from the repo root against `pytest.ini`; `pit_tests.py` is renamed to a discoverable name; CI Python is pinned to the image's 3.12; `KNOWN_ISSUES.md` gains entries for F-01/F-02/F-03/F-05/F-08; the research walk-forward corpus is wired to produce the `validated: bool` + metric fields that every promoted artifact must carry. **Closes F-09, F-03, F-19.**

### 13.8 Contract parity in the frontend

`forecast_eligibility` enters `types/contracts.ts` and the Decision page; the four raw-`fetch` hooks move to `apiClient`; `usePolling` is deleted; route-level code splitting and minification bring the 1.50 MB bundle under control. **Closes F-13, F-18.**

### 13.9 Governance cadence

Tag a v2.8 checkpoint once Wave 0 + Wave 1 of `report.md §12` land; bump `STABLE.md`; correct `README.md` (version header, language); finish or delete `informe.md`; keep `report.md` + `architecture.md` regenerated in the same commit whenever a served surface, an artifact, or a verification result changes.

---

*Cross-references: `report.md` (status, findings register F-01…F-23, recommendations), `KNOWN_ISSUES.md` (KI-001…KI-009, A3/A4/P1/B, Stub L4), `STABLE.md` (release registry), `informe.md` (macro/policy_diff audit, 2026-10-01).*
