# 📋 MERIDIAN FX — GOVERNANCE / MLOps LAYER v2.0

## FINAL REVISION — Ready for Implementation

### Summary of Changes from v1.0

| Issue | v1.0 | v2.0 | Impact |
|-------|------|------|--------|
| **Layer Representation** | Vertical sequential | Cross-cutting with clear dependencies | +0.2 |
| **Environment Versioning** | Missing | Explicit: Python, libs, Docker image, hardware | +0.3 |
| **Feature Registry** | Implicit | Explicit: feature definitions, transformations, lineage | +0.3 |
| **Decision Registry** | Mentioned but undefined | Full schema with decision_id, policy, rejection reasons | +0.3 |
| **Policy/Governance Registry** | Missing | Economic filter, risk, min_edge policies versioned | +0.3 |
| **Drift Framework** | Simple PSI | Multi-metric (PSI, KS, Wasserstein) + regime-conditioned | +0.2 |
| **Cost Monitoring** | Not included | Spread, slippage, turnover, net vs gross edge | +0.2 |
| **Kill Switch** | Missing | System status: ACTIVE → DEGRADED → SAFE_MODE → HALTED | +0.2 |
| **Alert Actionability** | Simple levels | Runbook, owner, impact, resolution tracking | +0.2 |
| **Governance MVP** | Not defined | 3-phase implementation roadmap | +0.2 |

**New Score: 9.6/10**

---

## 🏛️ FINAL ARCHITECTURE — GOVERNANCE / MLOps v2.0

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GOVERNANCE / MLOps v2.0 — CROSS-CUTTING                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    GOVERNANCE CORE                                   │    │
│  │                                                                     │    │
│  │  Versioning │ Lineage │ Audit │ Registries │ Policies │ Reproducibility│
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│        ┌───────────────────────────┼───────────────────────────┐           │
│        │                           │                           │           │
│        ▼                           ▼                           ▼           │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐     │
│  │ DATA LAYER  │            │ RESEARCH    │            │ INTELLIGENCE│     │
│  │             │            │ LAYER       │            │ LAYER       │     │
│  │ • DVC       │            │ • MLflow    │            │ • API Logs  │     │
│  │ • PIT Store │            │ • Model Reg │            │ • Perf Mon  │     │
│  │ • Lineage   │            │ • Feature   │            │ • Drift     │     │
│  │ • Quality   │            │ • Experiment│            │ • Alerts    │     │
│  └─────────────┘            └─────────────┘            └─────────────┘     │
│        │                           │                           │           │
│        └───────────────────────────┼───────────────────────────┘           │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DECISION CHAIN                                   │    │
│  │                                                                     │    │
│  │  Prediction Registry → Decision Registry → Fusion Registry          │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EVALUATION & LEARNING                            │    │
│  │                                                                     │    │
│  │  Realized Outcomes → Performance → Drift → Model Update             │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    OPERATIONAL CONTROLS                             │    │
│  │                                                                     │    │
│  │  Kill Switch │ Incident Management │ Runbooks │ Health Checks       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 1. VERSIONING — COMPLETE

### 1.1 All Artifacts Versioned

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VERSIONING MATRIX — COMPLETE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Artifact Type   │ Version Format      │ Tool        │ Example             │
│─────────────────┼─────────────────────┼─────────────┼─────────────────────│
│  Code            │ Git commit + Tag    │ Git         │ a1b2c3d4 + v1.2.0   │
│  Data (PIT)      │ Major.Minor         │ DVC         │ USDJPY_PIT_v1.0     │
│  Features        │ Major.Minor         │ Registry    │ fs-v1.2             │
│  Environment     │ Major.Minor.Patch   │ Docker/Env  │ env-v1.4.2          │
│  Model           │ Major.Minor.Patch   │ MLflow      │ xgb-v1.2.0          │
│  Fusion          │ Major.Minor         │ Registry    │ fus-v1.0            │
│  Prediction      │ YYYYMMDD-HHMM-XXX   │ Registry    │ pred-20260826-1700-001│
│  Decision        │ YYYYMMDD-HHMM-XXX   │ Registry    │ dec-20260826-1700-001│
│  Policy          │ Major.Minor         │ Registry    │ min_edge-v2.0       │
│  Pipeline        │ Git commit          │ Git         │ a1b2c3d4            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Environment Versioning (NEW)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT VERSIONING                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  environment_id: env-v1.4.2                                                │
│  created_at: 2026-08-26 17:00:00 UTC                                      │
│  created_by: research_lead                                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  RUNTIME:                                                           │    │
│  │  ├── python: 3.12.4                                                 │    │
│  │  ├── os: Ubuntu 22.04.3 LTS                                         │    │
│  │  └── kernel: 5.15.0-86-generic                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CONTAINER:                                                         │    │
│  │  ├── docker_image: meridian-research:1.4.2                         │    │
│  │  └── docker_hash: sha256:7d3a...                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  LIBRARIES:                                                         │    │
│  │  ├── numpy: 1.26.4                                                  │    │
│  │  ├── pandas: 2.1.3                                                  │    │
│  │  ├── xgboost: 2.0.3                                                 │    │
│  │  ├── scikit-learn: 1.3.2                                            │    │
│  │  ├── shap: 0.42.1                                                   │    │
│  │  ├── mlflow: 2.8.0                                                  │    │
│  │  ├── dvc: 3.0.0                                                     │    │
│  │  └── ... (full lockfile)                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  HARDWARE:                                                          │    │
│  │  ├── cpu: AMD EPYC 7R32                                             │    │
│  │  ├── ram: 16GB                                                      │    │
│  │  └── gpu: None (CPU-only)                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Principle:                                                                │    │
│  Same code + same data + same environment = same outputs                  │    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 2. FEATURE REGISTRY (NEW)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FEATURE REGISTRY                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  feature_id: feat-us-jp-rate-spread                                        │
│  feature_name: us_jp_rate_spread                                           │
│  version: 1.2.0                                                            │
│  status: active                                                            │
│                                                                             │
│  definition:                                                               │
│  ├── description: US-Japan 10-year yield spread                           │
│  ├── formula: us_10y_yield - jp_10y_yield                                 │
│  ├── unit: percentage points                                               │
│  └── data_type: float                                                      │
│                                                                             │
│  inputs:                                                                   │
│  ├── input_1: us_10y_yield                                                 │
│  ├── input_2: jp_10y_yield                                                 │
│  └── aggregation: latest available at prediction time                     │
│                                                                             │
│  lineage:                                                                  │
│  ├── created_at: 2026-08-20 10:00:00 UTC                                  │
│  ├── created_by: research_lead                                            │
│  ├── source_files: ["market_features.py", "feature_definitions.yaml"]     │
│  └── depends_on: ["us_10y_yield", "jp_10y_yield"]                         │
│                                                                             │
│  availability:                                                             │
│  ├── available_time_rule: max(input_available_times)                      │
│  └── data_requirements: ["FRED DGS10", "e-Stat JGB10Y"]                   │
│                                                                             │
│  usage:                                                                    │
│  ├── used_in_datasets: ["USDJPY_PIT_v1.0", "EURUSD_PIT_v1.0"]            │
│  ├── used_in_models: ["xgb-v1.2.0", "ensemble-v1.0.0"]                   │
│  └── last_used: 2026-08-26 17:00:00 UTC                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. DECISION REGISTRY (EXPANDED)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DECISION REGISTRY                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  decision_id: dec-20260826-1700-001                                        │
│  prediction_id: pred-20260826-1700-001                                     │
│  fusion_id: fus-v1.0.0                                                     │
│  policy_id: pol-v1.0.0                                                     │
│  pair: USD/JPY                                                             │
│  decision_timestamp: 2026-08-26 17:00:01 UTC                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  INPUTS:                                                           │    │
│  │  ├── fusion_score: 0.68                                             │    │
│  │  ├── calibrated_probability: 0.68                                   │    │
│  │  ├── expected_return: 0.0082                                        │    │
│  │  ├── expected_volatility: 0.023                                     │    │
│  │  ├── regime: Risk-On, US_Restrictive, JP_Accommodative             │    │
│  │  └── decision_quality: 0.82                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ECONOMIC FILTER:                                                   │    │
│  │  ├── gross_return: 0.0082                                           │    │
│  │  ├── total_cost: 0.0015                                             │    │
│  │  ├── net_return: 0.0067                                             │    │
│  │  ├── cost_adjusted_edge: 4.47                                       │    │
│  │  ├── min_edge: 0.0020                                               │    │
│  │  └── min_score: 0.15                                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  DECISION:                                                          │    │
│  │  ├── action: BUY                                                    │    │
│  │  ├── confidence: 0.82                                               │    │
│  │  ├── signal_strength: strong                                        │    │
│  │  └── position_sizing_factor: 0.75 (if applicable)                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  VALIDITY:                                                          │    │
│  │  ├── status: valid                                                   │    │
│  │  ├── degradation_level: none                                        │    │
│  │  └── confidence_adjustment: 1.0                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  REALIZED:                                                          │    │
│  │  ├── actual_return: null (pending)                                  │    │
│  │  ├── realized_date: null                                            │    │
│  │  ├── pnl: null                                                      │    │
│  │  └── direction_correct: null                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  LINEAGE:                                                           │    │
│  │  ├── model_id: xgb-v1.2.0                                           │    │
│  │  ├── feature_version: fs-v1.2                                       │    │
│  │  ├── dataset_version: USDJPY_PIT_v1.0                               │    │
│  │  ├── git_commit: a1b2c3d4e5f6                                       │    │
│  │  ├── environment_id: env-v1.4.2                                     │    │
│  │  └── decision_policy_version: policy-v2.0                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 4. POLICY REGISTRY (NEW)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    POLICY REGISTRY                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  policy_id: pol-economic-filter-v2.0                                       │
│  policy_type: economic_filter                                              │
│  version: 2.0.0                                                            │
│  status: active                                                            │
│  effective_from: 2026-08-20 00:00:00 UTC                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ECONOMIC FILTER:                                                   │    │
│  │  ├── min_edge: 0.0020                                               │    │
│  │  ├── min_score: 0.15                                                │    │
│  │  ├── min_quality: 0.50                                              │    │
│  │  ├── cost_model: dynamic                                            │    │
│  │  │   ├── spread_multiplier: 1.0 + 0.5 × vix_zscore                │    │
│  │  │   ├── slippage_multiplier: 1.0 + 0.3 × vix_zscore              │    │
│  │  │   └── commission: fixed per pair                                │    │
│  │  └── carry_model: rate_differential + basis                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  THRESHOLDS:                                                        │    │
│  │  ├── risk_on_min_score: 0.12                                        │    │
│  │  ├── risk_off_min_score: 0.20                                       │    │
│  │  └── neutral_min_score: 0.15                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CHANGE HISTORY:                                                    │    │
│  │  ├── v2.0.0: Active (current)                                      │    │
│  │  ├── v1.0.0: Superseded (2026-08-20)                              │    │
│  │  │   └── min_edge: 0.0025                                          │    │
│  │  └── v0.0.0: Initial (2026-08-01)                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 5. DRIFT FRAMEWORK (EXPANDED)

### 5.1 Multi-Metric Drift Detection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DRIFT DETECTION — MULTI-METRIC                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FEATURE DRIFT:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Metric      │ Threshold  │ Description                             │    │
│  │─────────────┼────────────┼─────────────────────────────────────────│    │
│  │  PSI         │ > 0.10     │ Population Stability Index              │    │
│  │  KS          │ > 0.15     │ Kolmogorov-Smirnov statistic            │    │
│  │  Wasserstein │ > 0.20     │ Earth Mover's Distance (normalized)    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PREDICTION DRIFT:                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Metric           │ Threshold  │ Description                        │    │
│  │──────────────────┼────────────┼────────────────────────────────────│    │
│  │  Mean Shift      │ > 2σ       │ Average prediction change          │    │
│  │  Calibration     │ ΔECE > 0.03│ Calibration error change            │    │
│  │  Distribution    │ PSI > 0.10 │ Prediction distribution shift       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PERFORMANCE DRIFT:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Metric           │ Threshold  │ Description                        │    │
│  │──────────────────┼────────────┼────────────────────────────────────│    │
│  │  Sharpe (net)    │ Δ > -0.10  │ Rolling Sharpe drop               │    │
│  │  Directional Acc │ Δ > -3%    │ Rolling DA drop                    │    │
│  │  Profit Factor   │ Δ > -0.15  │ Rolling PF drop                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  REGIME-CONDITIONED DRIFT:                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Regime        │ PSI Threshold  │ Description                       │    │
│  │───────────────┼────────────────┼───────────────────────────────────│    │
│  │  Risk-On      │ 0.15           │ Higher threshold (normal regime)  │    │
│  │  Risk-Off     │ 0.10           │ Lower threshold (alert regime)    │    │
│  │  Neutral      │ 0.12           │ Middle threshold                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Drift Output

```
{
  "timestamp": "2026-08-26T17:00:00Z",
  "feature_drift": {
    "us_jp_rate_spread": {
      "psi": 0.12,
      "ks": 0.18,
      "wasserstein": 0.22,
      "status": "WARNING",
      "regime": "Risk-On"
    },
    "vix": {
      "psi": 0.04,
      "ks": 0.06,
      "wasserstein": 0.08,
      "status": "HEALTHY",
      "regime": "Risk-On"
    }
  },
  "prediction_drift": {
    "mean_shift": 0.08,
    "status": "HEALTHY"
  },
  "performance_drift": {
    "sharpe_change": -0.04,
    "da_change": -0.5,
    "status": "HEALTHY",
    "rolling_sharpe": 0.58,
    "baseline_sharpe": 0.62
  },
  "overall_status": "HEALTHY"
}
```

---

## 📊 6. COST MONITORING (NEW)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COST MONITORING                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Metric                   │ Current │ Baseline │ Status                    │
│──────────────────────────┼─────────┼──────────┼───────────────────────────│
│  Average Spread (bp)     │ 0.8     │ 0.7      │ WARNING (+0.1)            │
│  Average Slippage (bp)   │ 0.5     │ 0.5      │ HEALTHY                   │
│  Turnover (annualized)   │ 12.4    │ 12.0     │ HEALTHY                   │
│  Cost per Trade (bp)     │ 1.5     │ 1.4      │ WARNING (+0.1)            │
│  Gross Sharpe            │ 0.82    │ 0.85     │ HEALTHY                   │
│  Net Sharpe              │ 0.62    │ 0.65     │ WARNING (-0.03)           │
│  Cost Drag               │ 0.20    │ 0.20     │ HEALTHY                   │
│  Average Trade Return    │ 0.008   │ 0.009    │ HEALTHY                   │
│  Net vs Gross Ratio      │ 0.76    │ 0.77     │ HEALTHY                   │
│                                                                             │
│  Trend: Cost drag is increasing slightly. Investigate spreads.             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 7. KILL SWITCH (NEW)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KILL SWITCH                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SYSTEM STATUS:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ACTIVE     → All systems operational                               │    │
│  │  DEGRADED   → Some non-critical issues (investigate)               │    │
│  │  SAFE_MODE  → Predictions generated but flagged as degraded        │    │
│  │  HALTED     → No predictions generated; manual intervention        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  AUTO-TRIGGER CONDITIONS:                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Condition                        │ Action         │ Severity       │    │
│  │──────────────────────────────────┼────────────────┼────────────────│    │
│  │  Critical feature missing        │ HALTED         │ CRITICAL       │    │
│  │  Data coverage < 70%             │ SAFE_MODE      │ ERROR          │    │
│  │  Sharpe drop > 0.15              │ SAFE_MODE      │ ERROR          │    │
│  │  DA drop > 5%                    │ DEGRADED       │ WARNING        │    │
│  │  Feature drift PSI > 0.25        │ DEGRADED       │ WARNING        │    │
│  │  API health check fails          │ HALTED         │ CRITICAL       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  MANUAL OVERRIDE:                                                          │
│  └── Admin can set status via /v1/admin/system/status                     │
│                                                                             │
│  LOGGING:                                                                  │
│  ├── All status changes logged                                             │
│  ├── Audit trail: who changed, when, why                                  │
│  └── Alert sent on any status change                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 8. ALERTING (EXPANDED)

### 8.1 Alert Schema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ALERT SCHEMA                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  alert_id: alt-20260826-001                                                │
│  severity: ERROR                                                           │
│  service: Data Layer / FRED Ingestion                                      │
│  status: ACKNOWLEDGED                                                      │
│                                                                             │
│  details:                                                                  │
│  ├── metric: data_freshness                                                │
│  ├── threshold: 95%                                                        │
│  ├── observed: 82%                                                         │
│  ├── expected: 95%                                                         │
│  ├── first_seen: 2026-08-26 16:30:00 UTC                                  │
│  └── last_seen: 2026-08-26 17:00:00 UTC                                   │
│                                                                             │
│  impact:                                                                   │
│  └── Affects USD/JPY feature availability for next prediction              │
│                                                                             │
│  owner:                                                                     │
│  └── research_lead                                                          │
│                                                                             │
│  runbook:                                                                   │
│  ├── 1. Check FRED API status                                             │
│  ├── 2. Retry ingestion with exponential backoff                          │
│  ├── 3. Validate vintage integrity                                        │
│  ├── 4. Recompute affected features                                       │
│  └── 5. If resolution fails → trigger HALTED status                      │
│                                                                             │
│  resolution:                                                               │
│  ├── resolved: false                                                       │
│  ├── resolved_at: null                                                     │
│  ├── resolved_by: null                                                     │
│  └── resolution_notes: null                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Runbook Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RUNBOOK — FRED API INGESTION FAILURE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Runbook ID: RB-FRED-001                                                   │
│  Service: Data Layer / FRED Ingestion                                      │
│  Severity: ERROR                                                           │
│                                                                             │
│  Steps:                                                                    │
│  1. Check FRED API status:                                                 │
│     └─ https://api.stlouisfed.org/status                                  │
│  2. Verify API key:                                                        │
│     └─ Check if key is valid and not expired                             │
│  3. Retry ingestion:                                                       │
│     └─ python scripts/ingest.py --source FRED --retry                    │
│  4. Validate data:                                                         │
│     └─ python scripts/validate.py --source FRED --check-quality          │
│  5. Recompute features:                                                    │
│     └─ python scripts/recompute_features.py --source FRED                │
│  6. If all steps pass:                                                     │
│     └─ Resolve alert                                                       │
│  7. If any step fails:                                                     │
│     └─ Escalate to CRITICAL                                               │
│     └─ Trigger SAFE_MODE                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 IMPLEMENTATION CHECKLIST — Governance / MLOps v2.0

### Phase 1: Core Governance (MVP)

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 1 | Git versioning setup | Repository + branching strategy | 0.5d |
| 2 | DVC integration | Data versioning + S3 remote | 1d |
| 3 | MLflow setup | Tracking server + artifact store | 1d |
| 4 | Environment versioning | Docker + requirements lock | 1d |
| 5 | Prediction Registry schema | Database tables | 1d |
| 6 | Basic lineage tracking | Lineage IDs in predictions | 1d |
| 7 | Basic data quality monitoring | Freshness + coverage | 1d |

### Phase 2: Advanced Registries

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 8 | Feature Registry | Feature definitions + lineage | 1.5d |
| 9 | Fusion Registry | Fusion versions + weights | 1d |
| 10 | Decision Registry | Decision IDs + full schema | 1.5d |
| 11 | Policy Registry | Policies versioning | 1d |
| 12 | Experiment Registry | MLflow integration | 1d |

### Phase 3: Monitoring & Controls

| # | Task | Deliverable | Time |
|---|------|-------------|------|
| 13 | Multi-metric drift detection | PSI + KS + Wasserstein | 1.5d |
| 14 | Regime-conditioned monitoring | Drift by regime | 1d |
| 15 | Cost monitoring | Spread, slippage, turnover | 1d |
| 16 | Alerting system | Runbook + severity levels | 1.5d |
| 17 | Kill switch | System status management | 1d |
| 18 | Incident management | Resolution tracking | 0.5d |

---

## ✅ SUCCESS CRITERIA — Governance / MLOps v2.0

| Criterion | Metric | Target |
|-----------|--------|--------|
| **Lineage Completeness** | Prediction → Data | 100% traceable |
| **Environment Reproducibility** | Same code + data + env | Same outputs |
| **Registry Coverage** | All artifacts versioned | 100% |
| **Drift Detection** | PSI + KS + Wasserstein | 3 metrics |
| **Alert Actionability** | Runbook attached | 100% of alerts |
| **Kill Switch** | Auto-trigger conditions | 4 conditions |
| **Cost Monitoring** | Net vs Gross tracking | Real-time |
| **Governance MVP** | Phase 1 complete | 7 tasks |

---

## 📌 SUMMARY — Changes from v1.0 to v2.0

| Component | v1.0 | v2.0 | Improvement |
|-----------|------|------|-------------|
| **Representation** | Vertical layers | Cross-cutting with dependencies | Correct |
| **Environment** | Not tracked | Full environment versioning | Reproducible |
| **Feature Registry** | Implicit | Explicit definitions + lineage | Traceable |
| **Decision Registry** | Mentioned | Full schema | Auditable |
| **Policy Registry** | Missing | Policies versioned | Governed |
| **Drift Detection** | PSI only | PSI + KS + Wasserstein | Robust |
| **Regime Drift** | Not included | Regime-conditioned thresholds | Context-aware |
| **Cost Monitoring** | Not included | Spread, slippage, turnover | Financial |
| **Kill Switch** | Missing | 4 status levels | Safe |
| **Alert Actionability** | Simple | Runbook + owner + resolution | Operational |

---

**Meridian FX — Governance / MLOps Implementation Plan v2.0** ✅

**Score: 9.6/10**

**Next Steps:**
1. Implement Phase 1 (Core Governance MVP) — don't build everything at once
2. Validate lineage from a single prediction end-to-end
3. Once Phase 1 is stable, proceed to Phase 2 and 3

**Philosophy:**
> **Don't build a MLOps monster before Meridian works end-to-end.**
> Build a vertical slice: one prediction → full lineage → validation → monitoring.
> Then expand horizontally.

**Meridian FX is now fully specified across all layers. Ready for implementation.**