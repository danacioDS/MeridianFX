# 📦 MERIDIAN FX — DATA ACQUISITION STRATEGY (FINAL VERSION)

**Version 1.0 — Ready for Implementation**

---

## 🧭 Guiding Principle

> **Meridian does not work with data. Meridian works with information available at a specific historical point in time.**

Every observation must answer:

> **What did the model know at time t, and why?**

---

## 🏗️ Data Architecture (3 Layers)

| Layer             | Purpose                           | Rule                                  |
| ----------------- | --------------------------------- | ------------------------------------- |
| **Raw**           | Store exactly what was downloaded | Never modified                        |
| **Normalized**    | Unify schemas, dates, and sources | Temporal metadata is added            |
| **Feature Store** | Data ready for the model          | **The model only queries this layer** |

---

## 📅 Universal Temporal Schema

Every series, without exception, must have these fields:

```
observation_date          → date the data refers to
release_datetime_utc      → official publication date/time (UTC)
available_datetime_utc    → date/time from which it is usable (UTC)
source_timezone           → source timezone (e.g. "America/New_York")
vintage_date              → data version (if applicable)
value                     → numerical value
revision_number           → 0 = first publication
is_initial_release        → TRUE if first release
is_stale                  → TRUE if forward-filled due to market closure
market_open_flag          → TRUE if the market was operating
source                    → primary source
url                       → link to the origin
retrieved_at_utc          → download date/time (UTC)
```

**Fundamental rule:**

> **Value known at t = f(available_datetime_utc ≤ t)**

---

## 🌐 Sources by Type

### A. Macroeconomic (SPMM + Balassa-Samuelson)

| Variable              | USA               | Japan                      | Frequency | Vintage |
| --------------------- | ----------------- | -------------------------- | --------- | ------- |
| CPI                   | BLS → FRED/ALFRED | Statistics Bureau → e-Stat | Monthly   | Yes     |
| GDP                   | BEA → FRED/ALFRED | Cabinet Office → e-Stat    | Quarterly | Yes     |
| 10Y Yield             | Treasury → FRED   | BoJ → FRED                 | Daily     | No      |
| Industrial Production | Fed → FRED        | METI → e-Stat              | Monthly   | Yes     |
| Productivity          | BLS → FRED        | JIP/RIETI → OECD           | Quarterly | Yes     |
| Unit Labor Cost       | BLS → FRED        | JILPT → OECD               | Quarterly | Yes     |
| PMI                   | ISM → FRED        | Jibun Bank → Markit        | Monthly   | No*     |

*** Note:** Although they do not have a formal "vintage," they do have `release_datetime_utc` and `available_datetime_utc`.

---

### B. Market and Risk

| Variable      | Source  | Alternative       | Frequency | Temporality          |
| ------------- | ------- | ----------------- | --------- | -------------------- |
| USD/JPY Spot  | BoJ/Fed | Yahoo Finance     | Daily     | No vintage           |
| VIX           | CBOE    | Yahoo Finance     | Daily     | No                   |
| Gold          | COMEX   | Yahoo Finance     | Daily     | No                   |
| Oil (WTI)     | NYMEX   | Yahoo Finance     | Daily     | No                   |
| TED Spread    | Fed     | FRED              | Daily     | No                   |
| JPY COT       | CFTC    | CFTC Bulk Exports | Weekly    | **Publication date** |
| Open Interest | CFTC    | CFTC Bulk Exports | Weekly    | **Publication date** |

**Critical rule:** CFTC is used with `release_datetime_utc`, **not** the contract date.

$$
COT_t = COT_{\max(\tau) : available(\tau) \le t}
$$

---

### C. RAG (Textual Information)

| Central Bank | Source                        | Format      | Challenge                      |
| ------------ | ----------------------------- | ----------- | ------------------------------ |
| Fed (FOMC)   | Statements, minutes, speeches | HTML/PDF    | Easy to scrape                 |
| BoJ          | Policy statements, speeches   | PDF (JP/EN) | Complex PDFs, OCR if necessary |
| BIS          | Governors' speeches           | HTML/PDF    | Secondary source               |

**RAG Schema:**

```
document_id 
central_bank              → Fed, BoJ 
document_type             → Statement, Minutes, Speech 
publication_datetime_utc  → official publication date/time 
document_available_at_utc → date/time the document becomes available 
feature_available_at_utc  → date/time the derived variable is ready 
nlp_model_version         → version of the NLP model used 
text_version              → version of the processed text 
raw_text_hash             → hash of the original text 
hawkish_score
dovish_score
policy_divergence
forward_guidance_change
surprise_vs_previous
inflation_concern
growth_concern
```

**RAG Flow:**

```
Original document 
       ↓
Publication timestamp (UTC)
       ↓
Text extraction (PDF → text, with OCR if necessary)
       ↓
Topic classification (inflation, growth, forward guidance)
       ↓
Generation of latent variables
       ↓
Storage with feature_available_at_utc
```

---

## 🧩 Source Hierarchy (Tiers)

| Level      | Type                    | Examples                                       | Use                                 |
| ---------- | ----------------------- | ---------------------------------------------- | ----------------------------------- |
| **Tier 1** | Official primary source | BEA, BLS, BoJ, CFTC, Fed, Cabinet Office, METI | Whenever possible                   |
| **Tier 2** | Reliable aggregator     | FRED, ALFRED, e-Stat, OECD                     | When Tier 1 is not practical        |
| **Tier 3** | Commercial vendor       | Bloomberg, Refinitiv                           | **Optional upgrade**, no dependency |
| **Tier 4** | Free source             | Yahoo Finance, Investing.com                   | For market data at no cost          |

**Rule:** Bloomberg is **not a requirement for the MVP**.

---

## ⚙️ Operational Rules

### 1. Forward-Fill (Holidays and Market Closures)

| Data Type                | Forward-fill               | `is_stale` Flag   |
| ------------------------ | -------------------------- | ----------------- |
| Bonds (JGB, Treasury)    | Yes                        | `TRUE` if holiday |
| FX Spot                  | **No**                     | Left as `NULL`    |
| VIX, Gold, Oil           | **No**                     | Left as `NULL`    |
| Macroeconomic (CPI, GDP) | Not applicable (step-wise) | `FALSE`           |

**Rule:**

> Forward-fill only when it conceptually represents the "last known value" and explicitly mark it with `is_stale = TRUE`.

---

### 2. Step-wise (Low-Frequency Data)

**Rule:**

> Macroeconomic data remains constant from `available_datetime_utc` until the next available publication, **while respecting revisions**.

```
Jan ─── Mar 
       │ 
       │ Q1 GDP still unknown
       │ 
Apr ───┤ GDP Q1 = 2.1 (is_initial_release = TRUE) 
       │ 
May ───┤ GDP Q1 = 2.3 (is_initial_release = FALSE, revision_number = 1)
```

**Prohibited:** Linear interpolation before the official release.

---

### 3. Timestamps and Timezones

**Rule:**

> All timestamps are stored in **UTC**, while preserving the source timezone.

```
timestamp_utc            → 2026-08-25T13:30:00Z 
source_timezone          → "America/New_York" 
```

---

### 4. BoJ PDF Processing

**Rule:**

> Include a **Format Normalization / Layout-Aware Parsing** sub-process specifically designed for multilingual PDFs in the RAG Raw layer before the topic classifier.

---

## 🔬 Quality Control and Reproducibility

Each download must include:

* **File hash** (integrity)
* **Download log** (date, source, parameters)
* **Schema version** (changes in definitions)
* **Automated leakage test**
* **Snapshots** (to avoid dependence on external sources)

---

## 🧪 Leakage Test (Requirement)

**Fundamental rule:**

> For any Feature Store row at `timestamp_utc = t`, **all variables** must satisfy:

> `available_datetime_utc ≤ t`

**Automated tests:**

| Test                        | Verifies                                                        |
| --------------------------- | --------------------------------------------------------------- |
| `test_no_lookahead_bias`    | No variable has `available_datetime_utc > t`                    |
| `test_cftc_release_date`    | COT uses `release_datetime_utc`, not contract date              |
| `test_no_backward_fill`     | No future information is used to fill gaps                      |
| `test_revision_consistency` | Revisions are only applied after their `available_datetime_utc` |

---

## 📊 Feature Store — Final Structure

```
timestamp_utc
usd_jpy_spot
usd_jpy_return_1d
usd_jpy_return_5d
us_jp_rate_spread
us_jp_inflation_diff
us_jp_gdp_diff
us_jp_pmi_diff
us_jp_productivity_diff
vix_level
vix_change
gold_price
oil_price
cot_jpy_net_position
cot_jpy_zscore
fed_hawkish_score
boj_hawkish_score
policy_divergence
regime_inflation
regime_growth
regime_risk
```

**Metadata associated with each variable (in a separate table):**

```
variable_name
available_datetime_utc
is_stale
is_initial_release
source
```

**Construction rules:**

* All variables use `available_datetime_utc`
* Differences (US - Japan) only when both are available
* Forward-fill for bonds with `is_stale = TRUE`
* Step-wise for low-frequency data

---

## 🔁 Execution Pipeline by Phase

### Phase 0 — Infrastructure

* Define Raw / Normalized / Feature Store schemas
* Configure access to FRED, ALFRED, e-Stat, OECD
* Configure automated CFTC downloads

### Phase 1 — USD/JPY (Quantitative MVP)

* Download all US and Japan macro series with vintages
* Download USD/JPY, VIX, Gold, Oil
* Download weekly COT
* Build historical Feature Store (2015–2026)
* Run **leakage tests**

**Experiment order:**

```
E0   Random Walk 
E0b  Random Walk + Drift 
E1a  AR / ARIMA 
E1b  Elastic Net          ← Fundamental control for H1
E2a  XGBoost (without constraints) 
E2b  XGBoost + Monotonic Constraints 
E3   + Market Features 
E4   + Regime 
E5   + RAG 
E6   Walk-Forward (Expanding / Rolling) 
E7   Ensemble (XGBoost + LSTM) 
```

### Phase 2 — RAG Agent

* Scrape Fed and BoJ statements
* Process texts and generate latent variables
* Incorporate into the Feature Store
* Run **E5**

### Phase 3 — Multi-currency

* EUR, GBP, BRL, MXN, CNY, ARS, BOB
* Adjust sources by country

---

## 🎯 Conclusion

This strategy:

* ✅ Meets point-in-time and anti-leakage requirements
* ✅ Covers the US and Japan with primary sources
* ✅ Eliminates costly dependencies (Bloomberg)
* ✅ Integrates RAG as versioned, quantifiable variables
* ✅ Handles holidays, mixed frequencies, and complex PDFs
* ✅ Distinguishes initial releases from revisions
* ✅ Uses UTC with source timezone traceability
* ✅ Includes Elastic Net as an experimental control
* ✅ Guarantees historical reproducibility
* ✅ Scales to multiple currencies

---

> **Meridian FX already has its data backbone. The next step is to build the first Point-in-Time USD/JPY Dataset for 2015–2026 and demonstrate that no observation at `t` uses information with `available_datetime_utc > t`.**

---

**Version: 1.0 — Ready for Implementation** ✅
