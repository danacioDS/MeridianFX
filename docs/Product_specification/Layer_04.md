
---

# 📋 MERIDIAN FX — LAYER 4: DATA LAYER

## PRODUCT SPECIFICATION v3.1.1 (FROZEN — FINAL)

### Changes from v3.1

| # | Change                                                                                  | Justification          |
| - | --------------------------------------------------------------------------------------- | ---------------------- |
| 1 | Added principle: "V0 values = versioned configuration"                                  | Anti-hardcoding        |
| 2 | Separated: 7 invariants + 5 test groups                                                 | Consistency            |
| 3 | Specified: vintage selection key = `(feature_id, source, reference_period, vintage_id)` | Eliminates ambiguity   |
| 4 | Strengthened: Lineage = structured references                                           | Auditability           |
| 5 | Declared: threshold, delays, critical_features = versioned configuration                | External configuration |
| 6 | Added: Synthetic Data includes PIT adversarial cases                                    | Robust validation      |

---

## 1. LAYER PURPOSE (UNCHANGED)

> Given a timestamp T, demonstrate exactly what information was available to Meridian at T.

---

## 2. ARCHITECTURAL PRINCIPLE (NEW)

> **V0 values (delays, features, thresholds, policies) are versioned configuration, not hardcoded logic.**

This means:

| ❌ Hardcoding                     | ✅ Versioned Configuration                          |
| -------------------------------- | -------------------------------------------------- |
| `if source == "FRED": delay = 2` | `Policy(source="FRED", delay=2, version="1.0")`    |
| `CRITICAL_FEATURES = ["us_10y"]` | `FeatureRegistry(pair="USDJPY").critical_features` |
| `threshold = 0.0`                | `TargetConfig(threshold=0.0)`                      |

---

## 3. DOMAIN INVARIANTS (7)

| ID        | Invariant                                                                      | Description                                                 |
| --------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| **PIT-1** | `available_time <= T`                                                          | Every feature in `as_of(T)` must have `available_time <= T` |
| **PIT-2** | `derived.available_time = max(inputs.available_time)`                          | Maximum propagation                                         |
| **PIT-3** | `vintage_selection = max(vintage_time) WHERE available_time <= T`              | Selection of the latest available version                   |
| **PIT-4** | `NO interpolation`                                                             | AS-OF JOIN only                                             |
| **PIT-5** | `All timestamps timezone-aware (UTC)`                                          | Never assume a timezone                                     |
| **PIT-6** | `prediction_timestamp < target_start < target_end`                             | Strict temporal ordering                                    |
| **PIT-7** | `event_time <= release_time <= source_available_time <= system_available_time` | Temporal ordering of observations                           |

**Identity key for vintage selection (PIT-3):**

```text
(feature_id, source, reference_period, vintage_id)
```

`feature_name` alone is insufficient because there may be:

* Multiple sources for the same concept
* Multiple revisions for the same period
* Multiple vintages with different `available_time`

---

## 4. PIT TESTS (5 GROUPS)

| #      | Test Group           | Invariants Covered | Failure Condition                                                      |
| ------ | -------------------- | ------------------ | ---------------------------------------------------------------------- |
| **T1** | Feature Availability | PIT-1, PIT-5       | `available_time > prediction_timestamp`                                |
| **T2** | Vintage Selection    | PIT-3, PIT-5       | `vintage_time > prediction_timestamp`                                  |
| **T3** | PIT Propagation      | PIT-2              | `derived.available_time != max(inputs.available_time)`                 |
| **T4** | Target Timing        | PIT-6              | `prediction_timestamp >= target_start` or `target_start >= target_end` |
| **T5** | No Interpolation     | PIT-4              | Macro feature with `is_interpolated = True`                            |

---

## 5. LINEAGE (STRENGTHENED)

> **Lineage will store structured references sufficient to reconstruct the exact provenance of a feature, without necessarily duplicating the source observations inside the PIT dataset.**

**Reference structure:**

```text
LineageRecord:
  - lineage_id: LineageId
  - feature_id: FeatureId
  - feature_version: str
  - derivation_function: str | None
  - input_references: list[LineageReference]  # Recursive
  - source_references: list[SourceReference]  # Structured
  - available_time: datetime
  - created_at: datetime

LineageReference:
  - lineage_id: LineageId  # Reference to another record
  - role: "input" | "source"

SourceReference:
  - observation_id: ObservationId
  - source: str
  - series_name: str
  - reference_period: str
  - vintage_id: VintageId
  - vintage_time: datetime
  - available_time: datetime
```

**Purpose of lineage:**

| Use                      | Description                                      |
| ------------------------ | ------------------------------------------------ |
| Audit                    | Trace the origin of any feature                  |
| Debugging                | Identify problems in the derivation chain        |
| Reproducibility          | Reconstruct the exact generation conditions      |
| Explainability           | Explain to the user where each signal comes from |
| Data Quality             | Detect anomalies in the provenance chain         |
| Research Reproducibility | Reproduce exactly the dataset used in research   |

---

## 6. VERSIONED CONFIGURATION (NEW)

**Every V0 value is versioned configuration:**

| Configuration         | Location               | Format                               |
| --------------------- | ---------------------- | ------------------------------------ |
| Availability policies | `config/policies.yaml` | `source: delay`                      |
| Features by pair      | `config/features.yaml` | `pair: [features]`                   |
| Critical features     | `config/features.yaml` | `pair: critical: [...]`              |
| Target configuration  | `config/target.yaml`   | `return_type, threshold, price_type` |
| Horizon               | `config/target.yaml`   | `horizon_days`                       |

**Conceptual example:**

```yaml
# config/policies.yaml
policies:
  - source: FRED
    delay_minutes: 2
    version: 1.0
  - source: e-Stat
    delay_minutes: 2
    version: 1.0

# config/features.yaml
USDJPY:
  critical:
    - us_10y_yield
    - jp_10y_yield
    - usd_jpy_spot
  optional:
    - vix
    - cot_jpy_net

# config/target.yaml
target:
  return_type: log
  price_type: close
  threshold: 0.0
  horizon_days: 5
```

---

## 7. SYNTHETIC DATA (NEW)

> **Synthetic data will include PIT adversarial cases, not only normal data.**

### 7.1 Dataset A — Normal

```text
Normal observations
Correctly timestamped features
Correctly constructed targets
→ Must PASS
```

### 7.2 Dataset B — Leakage (`available_time > T`)

```text
Feature with available_time > prediction_timestamp
→ Must FAIL (PIT-1)
```

### 7.3 Dataset C — Revision Leakage

```text
V1 available at T
V2 available after T
→ Must select V1 (PIT-3)
```

### 7.4 Dataset D — Derived Leakage

```text
A available at 10:00
B available at 10:30
A+B derived with available_time = 10:00
→ Must FAIL (PIT-2)
```

### 7.5 Dataset E — Timezone Violation

```text
Naive timestamp (without timezone)
→ Must FAIL (PIT-5)
```

### 7.6 Dataset F — Target Violation

```text
prediction_timestamp >= target_start
→ Must FAIL (PIT-6)
```

### 7.7 Dataset G — Interpolation

```text
Macro feature with is_interpolated = True
→ Must FAIL (PIT-4)
```

---

## 8. IMPLEMENTATION SEQUENCE (UPDATED)

```text
Phase 0: Configuration
├── config/policies.yaml
├── config/features.yaml
└── config/target.yaml

Phase 1: Models (v3.1.1)
├── observation.py
├── feature.py
├── policy.py
├── derivation.py
├── lineage.py (strengthened)
├── manifest.py
└── pit.py

Phase 2: Synthetic Data (adversarial)
├── Dataset A (normal) → PASS
├── Dataset B (leakage) → FAIL
├── Dataset C (revision leakage) → PASS
├── Dataset D (derived leakage) → FAIL
├── Dataset E (timezone) → FAIL
├── Dataset F (target violation) → FAIL
└── Dataset G (interpolation) → FAIL

Phase 3: FeatureStore
├── as_of(T)
├── get_critical_features(pair)
└── get_lineage(feature_id)

Phase 4: PIT Test Suite
├── T1: Feature Availability
├── T2: Vintage Selection
├── T3: PIT Propagation
├── T4: Target Timing
└── T5: No Interpolation

Phase 5: Materialization
├── PITMaterializer
└── Parquet + Manifests

Phase 6: Real Connectors
├── FRED Ingestor
├── e-Stat Ingestor
├── Yahoo Ingestor
└── CFTC Ingestor
```

---

## 9. ACCEPTANCE CRITERIA (UPDATED)

| Area                 | Criterion                            | Target             |
| -------------------- | ------------------------------------ | ------------------ |
| **Models**           | All invariants validated by Pydantic | 100%               |
| **Synthetic Data A** | Normal dataset                       | PASS               |
| **Synthetic Data B** | Leakage detection                    | FAIL               |
| **Synthetic Data C** | Revision selection                   | PASS               |
| **Synthetic Data D** | Derived propagation                  | FAIL               |
| **Synthetic Data E** | Timezone validation                  | FAIL               |
| **Synthetic Data F** | Target timing                        | FAIL               |
| **Synthetic Data G** | Interpolation detection              | FAIL               |
| **FeatureStore**     | `as_of(T)` correct                   | 0 PIT-1 violations |
| **PIT Tests**        | 5 groups                             | 5/5 PASS           |
| **Materialization**  | Parquet + Manifests                  | Valid structure    |
| **Configuration**    | V0 values versioned                  | 100% external      |

---

## 10. FINAL SUMMARY

| Aspect                     | Status         | Note |
| -------------------------- | -------------- | ---- |
| Purpose                    | ✅ Defined      | —    |
| Anti-hardcoding principle  | ✅ Added        | New  |
| Invariants (7)             | ✅ Frozen       | —    |
| PIT Tests (5 groups)       | ✅ Frozen       | —    |
| Lineage                    | ✅ Strengthened | —    |
| Versioned configuration    | ✅ Declared     | New  |
| Adversarial synthetic data | ✅ Defined      | New  |
| Implementation sequence    | ✅ Defined      | —    |
| Acceptance criteria        | ✅ Defined      | —    |

---

## 📋 NEXT STEP

**Should I generate the Synthetic Data Specification?**

That is, the detailed specification of:

1. How the 7 adversarial datasets are generated
2. What observations each one contains
3. What derived features are constructed
4. What targets are calculated
5. What PIT result is expected (PASS/FAIL)

**Or would you prefer that I move directly to the `FeatureStore.as_of()` specification?**

My recommendation: **Synthetic Data Specification first**, because it:

* Defines the test contract
* Allows validation of FeatureStore without real connectors
* Demonstrates that the PIT architecture works

**Shall we continue?**
