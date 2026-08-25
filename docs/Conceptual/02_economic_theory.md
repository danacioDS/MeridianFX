# Meridian FX — Quantitative Research Base Document (Final Version 1.0)

---

## 📌 Executive Summary

**Meridian FX** is an experimental financial intelligence platform that investigates exchange-rate predictability through an incremental approach. The project is structured as applied research that tests the central hypothesis that **macroeconomic fundamentals have predictive power over exchange rates, but their relationship is nonlinear, regime-dependent, and time-varying.**

The experimental design follows an **incremental layer architecture (ablation study)**, where each component is added sequentially and evaluated against a common benchmark: the **Random Walk**. This makes it possible to answer the fundamental question in the financial literature:

> **How much additional information does each component of the system provide over the random walk, and under which economic conditions does it perform best?**

---

## 🧠 Economic Foundation

### The Meese-Rogoff Paradox (1983)

The starting point for Meridian FX is one of the most famous empirical findings in financial econometrics:

> **"Traditional macroeconomic models do not systematically outperform a simple random walk in short-term exchange-rate forecasting."**

This finding, known as the **"Exchange Rate Determination Puzzle,"** has been replicated for decades. Macroeconomic fundamentals *should* explain exchange-rate movements, but empirically they do not perform well at short horizons.

**The Meridian hypothesis**: The paradox is not a dead end, but an **opportunity**. Linear models fail because the relationship between fundamentals and exchange rates is:

1. **Nonlinear** — effects are neither constant nor proportional

2. **Regime-dependent** — the same factor has different effects depending on the state of the economy

3. **Time-varying** — the relationship changes structurally over time

---

### The Theories Supporting the System

#### 1. The Sticky-Price Monetary Model (SPMM — Dornbusch, 1976)

**Postulate**: Exchange rates are determined by differentials in:

* Inflation
* Interest rates
* Money supply
* GDP growth

**Implementation in Meridian**: Features based on macroeconomic differentials (US-JP yield spread, US-JP inflation differential), which represent the operational translation of the SPMM.

**Methodological Note**: The relationship between differentials and exchange rates should not be treated as a structural law that always holds in the short run. Its direction may vary depending on the economic regime and time horizon.

#### 2. The Balassa-Samuelson Effect (1964)

**Postulate**: Productivity differentials between sectors (tradable vs. non-tradable) explain differences in price levels and, therefore, in the real exchange rate.

**Implementation in Meridian**: Relative productivity, output per worker, and manufacturing productivity features. GDP and PMI function as **proxies for the economic cycle**, rather than direct measurements of the Balassa-Samuelson effect.

#### 3. The Macro Regime as a State Variable

**Postulate**: The impact of fundamentals on exchange rates depends on the **macroeconomic regime** in which the economy operates (Hamilton, 1989; Sims, 1999).

**Implementation in Meridian**: The **Macro Agent** classifies the regime, and this classification is used as a feature or model selector.

---

## 🧪 Experimental Design: Falsifiable Hypotheses

Meridian FX is structured as an **incremental experiment** with clearly defined hypotheses:

### H1 — Nonlinearity

> **A nonlinear model based on fundamentals outperforms an equivalent linear model out of sample.**

**Comparison**: XGBoost vs Elastic Net (same fundamentals, different specification).

### H2 — Regime

> **Incorporating the macroeconomic regime improves predictive performance relative to a model that ignores the regime.**

**Comparison**: XGBoost without regime vs XGBoost with regime.

### H3 — Non-Fundamental Information

> **VIX, yields, commodities, positioning, and liquidity variables provide incremental information beyond macroeconomic fundamentals.**

**Comparison**: XGBoost with fundamentals only vs XGBoost with fundamentals + market features.

### H4 — Textual Information (RAG)

> **Information extracted from central-bank documents adds predictive power after controlling for macroeconomic and financial variables.**

**Comparison**: XGBoost + Regime + Market vs XGBoost + Regime + Market + RAG.

### H5 — Temporal Adaptation

> **Walk-forward + retraining outperforms a static model trained only once.**

**Comparison**: Static model vs periodically retrained model.

### H6 — Absolute Benchmark

> **Meridian generates statistically significant out-of-sample predictive and economic power relative to the Random Walk after transaction costs and remains stable across different regimes and subperiods.**

**Comparison**: Full Meridian FX vs Random Walk.

---

## 🏗️ Experimental Evaluation Pipeline

### Data Structure and Anti-Leakage

To validate $H_5$ (temporal adaptation) and avoid *look-ahead bias*, the data split must be strictly sequential and respect macroeconomic release frequencies:

| Period                | Purpose                                                 |
| --------------------- | ------------------------------------------------------- |
| **2015 – 2021**       | Train Period (Static / First Fold)                      |
| **2022 – 2023**       | Validation Period (Hyperparameter Tuning)               |
| **2024 – 2026**       | Out-of-Sample / Walk-Forward Test                       |
| **Retraining Window** | Rolling Window blocks of 6 months or *Expanding Window* |

**Golden Rule**: Each feature must use only information that would actually have been available at that point in time. This requires correctly handling macroeconomic data release dates.

**Point-in-Time Data**: Point-in-Time series (*vintages*) will be used to ensure that model training at time $t$ uses only the CPI/GDP value that was publicly available at $t$, ignoring subsequent revisions.

**Dataset Structure**:

```text
observation_date
release_date
available_date
revision_date
```

### Incremental Experiment Matrix (Ablation Study)

| ID      | Experiment                  | Core Model                      | Dominant Feature Set                   | Theoretical Purpose                                             |
| ------- | --------------------------- | ------------------------------- | -------------------------------------- | --------------------------------------------------------------- |
| **E0**  | Benchmark                   | Random Walk                     | N/A ($S_t$)                            | Starting point of Meese-Rogoff                                  |
| **E0b** | Benchmark + Drift           | Random Walk + Drift             | N/A ($S_t + \mu$)                      | More robust benchmark                                           |
| **E1a** | Autoregressive Model        | AR / ARIMA                      | Temporal dynamics                      | Capture autocorrelation                                         |
| **E1b** | Linear Model                | Elastic Net                     | SPMM differentials                     | Test whether the classical linear approach provides signal      |
| **E2a** | Nonlinearity ($H_1$)        | XGBoost (without constraints)   | SPMM + Balassa-Samuelson differentials | Measure the gain from tree-based models                         |
| **E2b** | Nonlinearity + Theory       | XGBoost + Monotonic Constraints | SPMM + Balassa-Samuelson differentials | Measure the effect of imposing economic theory                  |
| **E3**  | Market Data ($H_3$)         | XGBoost                         | Macro + VIX, Gold, Oil, COT, TED       | Measure the impact of liquidity and risk aversion               |
| **E4**  | Regime ($H_2$)              | XGBoost / Regime Selector       | E3 + Macro Agent state labels          | Test whether the regime acts as a state variable                |
| **E5**  | Textual Information ($H_4$) | XGBoost + NLP Features          | E4 + Sentiment Spread (Fed vs BoJ)     | Determine the incremental information provided by the RAG Agent |
| **E6a** | Adaptation (Expanding)      | XGBoost Walk-Forward            | E5 with Expanding Window               | Evaluate concept drift                                          |
| **E6b** | Adaptation (Rolling)        | XGBoost Walk-Forward            | E5 with Rolling Window 6M              | Measure sensitivity to recent data                              |
| **E7**  | Ensemble Candidate ($H_6$)  | XGBoost + LSTM                  | E6 + Embeddings / Temporal Sequences   | Capture short- and long-term memory dynamics                    |

### Note on Monotonic Constraints

Monotonic constraints are treated as **an experimental hypothesis** (E2b), rather than an assumed truth. This makes it possible to investigate:

> **Do economic constraints improve generalization in some regimes while reducing flexibility in others?**

---

## 📊 Technical Feature Specification

### Fundamental Features (SPMM + Balassa-Samuelson)

| Feature                            | Theory                  | Expected Direction | Monotonic Constraint (E2b) |
| ---------------------------------- | ----------------------- | ------------------ | -------------------------- |
| US-JP 10Y Yield Spread             | SPMM                    | Positive (+)       | Positive monotonic         |
| US-JP Inflation Differential       | PPP                     | Negative (-)       | Negative monotonic         |
| US-JP GDP Growth Differential      | SPMM                    | Positive (+)       | Positive monotonic         |
| US-JP PMI Differential             | SPMM                    | Positive (+)       | Positive monotonic         |
| US-JP Productivity Differential    | Balassa-Samuelson       | Positive (+)       | Positive monotonic         |
| US-JP Unit Labor Cost Differential | Balassa-Samuelson       | Negative (-)       | Negative monotonic         |
| US-JP Real Yield Spread            | Inflation-adjusted SPMM | Positive (+)       | Positive monotonic         |

### Market Features

| Feature                | Theory                   | Expected Direction           |
| ---------------------- | ------------------------ | ---------------------------- |
| VIX                    | Risk-off / Safe Haven    | Negative (-)                 |
| VIX Change             | Risk-off / Safe Haven    | Negative (-)                 |
| Gold Price             | Risk-off / Safe Haven    | Variable (safe haven)        |
| Oil Price              | Commodity terms of trade | Variable (country-dependent) |
| Momentum (20d)         | Persistence              | Positive (+)                 |
| CFTC Positioning (JPY) | Capital flows            | Negative (-) for USD/JPY     |
| TED Spread             | Global liquidity         | Negative (-)                 |

### Regime Features (Macro Agent)

| Regime           | Variables Defining It                               |
| ---------------- | --------------------------------------------------- |
| Inflation Regime | CPI > 3% (or > target + 1%)                         |
| Growth Regime    | GDP < 1% (recession) or > 3% (expansion)            |
| Risk Regime      | VIX > 25 (risk-off) or < 18 (risk-on)               |
| Policy Regime    | Real rate > 1% (restrictive) or < 0 (accommodative) |

### RAG Features (Textual Information)

Instead of simple "sentiment," the RAG Agent generates **latent economic variables**:

| Feature                   | Construction                                    | Purpose                                     |
| ------------------------- | ----------------------------------------------- | ------------------------------------------- |
| Fed Sentiment             | Hawkish/dovish classification of communications | Capture monetary-policy intent              |
| BoJ Sentiment             | Hawkish/dovish classification of communications | Capture monetary-policy intent              |
| Policy Divergence         | Fed Sentiment - BoJ Sentiment                   | Measure divergence between central banks    |
| Forward Guidance Surprise | Change in tone vs expectations                  | Capture changes in the expected policy path |
| Inflation Concern         | Mentions of inflation in communications         | Measure inflation concerns                  |
| Growth Concern            | Mentions of growth in communications            | Measure recession concerns                  |

---

## 📈 Evaluation Metrics

### Statistical Metrics

| Metric                               | Description                                                          | Purpose                                   |   |                     |
| ------------------------------------ | -------------------------------------------------------------------- | ----------------------------------------- | - | ------------------- |
| **Directional Accuracy (Hit Ratio)** | $\frac{1}{N}\sum \mathbb{I}(\text{sign}(\hat{y}) == \text{sign}(y))$ | Does it get the direction right?          |   |                     |
| **RMSE**                             | $\sqrt{\frac{1}{N}\sum (y_i - \hat{y}_i)^2}$                         | Magnitude accuracy                        |   |                     |
| **MAE**                              | $\frac{1}{N}\sum                                                     | y_i - \hat{y}_i                           | $ | Mean absolute error |
| **Log Loss / Brier Score**           | For probabilistic predictions                                        | Probability calibration                   |   |                     |
| **Information Coefficient**          | $IC_t = Corr(\hat r_t,r_t)$                                          | Correlation between prediction and return |   |                     |

### Statistical Tests

| Test                               | Purpose                                                   |
| ---------------------------------- | --------------------------------------------------------- |
| **Diebold-Mariano Test**           | Compare predictive accuracy between models in time series |
| **Bootstrap Confidence Intervals** | Evaluate metric robustness                                |

### Financial Metrics

| Metric                                  | Description                                                     | Purpose                       |
| --------------------------------------- | --------------------------------------------------------------- | ----------------------------- |
| **Annualized Sharpe Ratio**             | $SR = \frac{\mathbb{E}[R_p - R_f]}{\sigma_p} \times \sqrt{252}$ | Risk-adjusted return          |
| **Sortino Ratio**                       | Similar to Sharpe but penalizes only downside risk              | Downside risk                 |
| **Calmar Ratio**                        | $\frac{\text{Annual Return}}{\text{Max Drawdown}}$              | Return adjusted for drawdown  |
| **Information Ratio**                   | $\frac{\alpha}{\text{Tracking Error}}$                          | Risk-adjusted relative return |
| **Maximum Drawdown (Max DD)**           | Maximum loss from a peak to a trough                            | Maximum loss risk             |
| **Profit Factor**                       | $\frac{\sum \text{Gross Profits}}{\sum \text{Gross Losses}}$    | Profit/loss relationship      |
| **Performance after transaction costs** | Sharpe adjusted for spreads + slippage                          | Economic viability            |

### Trading Signal (Decision Rule)

The probability $P(\Delta FX_{t+h} > 0 | X_t, R_t)$ is converted into a market position using a neutrality band to avoid *over-trading*:

$$\text{Position}_t = \begin{cases} +1 & \text{if } P > 0.55 \ -1 & \text{if } P < 0.45 \ 0 & \text{otherwise} \end{cases}$$

### Results Matrix

```text
                         RW   AR   EN   XGB   XGB+MKT   XGB+REG   +RAG   ENS

────────────────────────────────────────────────────────────────────────────

Directional Accuracy

RMSE

MAE

Log Loss

IC

Sharpe

Sortino

Calmar

Max Drawdown

Profit Factor

DM Test (vs RW)

────────────────────────────────────────────────────────────────────────────

2015-2018

2019-2021

2022-2023

2024-2026

Risk-on

Risk-off

High inflation

Low inflation

```

---

## 🏗️ Agent Architecture (Implementation)

```text
                    ┌─────────────────────────────────────┐
                    │        GLOBAL ECONOMY              │
                    └─────────────────┬───────────────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
         MACRO DATA               MARKET DATA              TEXT DATA
             │                        │                        │
             ▼                        ▼                        ▼
       ┌───────────┐           ┌───────────┐           ┌───────────┐
       │   MACRO   │           │   QUANT   │           │    RAG    │
       │   AGENT   │           │   AGENT   │           │   AGENT   │
       └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
             │                        │                      │
             ▼                        │                      ▼
       REGIME STATE                   │                POLICY SIGNAL
             │                        │                      │
             └────────────────┬───────┴──────────────────────┘
                              ▼
                    ┌─────────────────────────────────────┐
                    │     DECISION FUSION ENGINE          │
                    │   (Combines: Regime + Forecast      │
                    │    + Policy Signal + SHAP)           │
                    └─────────────────┬───────────────────┘
                                      ▼
                    ┌─────────────────────────────────────┐
                    │        FORECAST + EXPLANATION       │
                    │   • P(up/down)                      │
                    │   • Expected Move                   │
                    │   • Confidence                       │
                    │   • SHAP Economic Explanation       │
                    └─────────────────────────────────────┘
```

### Agent Roles

| Agent               | Question It Answers                                                    | Method                                              |
| ------------------- | ---------------------------------------------------------------------- | --------------------------------------------------- |
| **Macro Agent**     | What state is the economy in?                                          | Regime classification (rules + statistical methods) |
| **Quant Agent**     | What does the quantitative evidence say?                               | XGBoost + LSTM + SHAP                               |
| **RAG Agent**       | What are central banks communicating that is not captured by the data? | Extraction of latent economic variables             |
| **Decision Fusion** | How do we combine these signals?                                       | Weighted integration                                |
| **Analyst Agent**   | Why did we reach this conclusion?                                      | SHAP-based economic explanation                     |

### Design Principle

**The LLM sits on top of the evidence; it does not generate the evidence.**

---

## 🔬 The Role of the RAG Agent in the Economic Thesis

The RAG Agent addresses a specific empirical question:

> **Does textual information from central-bank communications add predictive power after controlling for macroeconomic and financial variables?**

This constitutes a **particularly interesting applied extension** of the exchange-rate predictability problem.

**RAG Agent Hypotheses**:

* The tone of communications (hawkish/dovish) captures **monetary-policy intent** that is not fully reflected in published data.

* **Divergence** between central banks (e.g., Fed hawkish vs BoJ dovish) is an especially powerful predictor.

* **Forward-guidance surprises** capture changes in the expected policy path.

---

## 📋 Implementation Plan (MVP)

### Phase 1: Experimental Foundation (USD/JPY)

| Week  | Phase      | Activities                                          |
| ----- | ---------- | --------------------------------------------------- |
| **1** | Data Layer | Preparation of point-in-time data, anti-leakage     |
| **2** | Benchmarks | Random Walk, Random Walk + Drift, ARIMA             |
| **3** | E1-E2      | Elastic Net, XGBoost (with and without constraints) |
| **4** | E3         | XGBoost + Market Features                           |
| **5** | E4-E5      | XGBoost + Regime, XGBoost + RAG                     |
| **6** | E6         | Walk-Forward (Expanding + Rolling)                  |
| **7** | E7         | Ensemble Candidate (XGBoost + LSTM)                 |
| **8** | Evaluation | Results matrix, Diebold-Mariano, regime analysis    |

### Phase 2: Scaling (Multi-Currency)

| Week   | Phase                     | Activities                                                 |
| ------ | ------------------------- | ---------------------------------------------------------- |
| **9**  | EUR/USD                   | Repeat experimental pipeline                               |
| **10** | GBP/USD                   | Repeat experimental pipeline                               |
| **11** | USD/BRL                   | Repeat experimental pipeline (with commodity features)     |
| **12** | USD/MXN                   | Repeat experimental pipeline                               |
| **13** | USD/CNY                   | Repeat experimental pipeline (with intervention features)  |
| **14** | USD/ARS                   | Repeat experimental pipeline (with inflation features)     |
| **15** | USD/BOB                   | Repeat experimental pipeline (with dollarization features) |
| **16** | Dashboard + Documentation | Currency Radar, Morning Brief, final report                |

---

## 🎯 The Value of Meridian FX

Meridian FX is not merely a machine-learning project about currencies. It is **applied research** that:

1. **Tests** the hypothesis that ML models can capture the nonlinear relationship between fundamentals and exchange rates.

2. **Implements** the idea that the macroeconomic regime is a state variable that modifies the impact of fundamentals.

3. **Investigates** whether textual information from central banks adds incremental predictive power.

4. **Demonstrates** that explainability (SHAP) is essential in finance, where a "black box" is not acceptable.

5. **Validates** the importance of non-fundamental predictors (VIX, capital flows) in short-term exchange-rate dynamics.

6. **Recognizes** that the relationship between fundamentals and exchange rates is unstable over time, requiring retraining and walk-forward validation.

---

## 📝 Conclusion

Meridian FX is a **rigorous, elegant, and highly professional framework** that transforms a technical ML project into a formal methodological experiment designed to test falsifiable economic hypotheses.

**The central question Meridian can answer**:

> **How much additional information does each component of the system provide over the random walk, and under which economic conditions does it perform best?**

---

## 📚 Theoretical References

| Author(s)         | Year | Contribution                         |
| ----------------- | ---- | ------------------------------------ |
| Meese & Rogoff    | 1983 | Exchange-rate predictability paradox |
| Dornbusch         | 1976 | Sticky-Price Monetary Model (SPMM)   |
| Balassa           | 1964 | Balassa-Samuelson Effect             |
| Samuelson         | 1964 | Balassa-Samuelson Effect             |
| Hamilton          | 1989 | Regime Models (Markov Switching)     |
| Sims              | 1999 | State Variables in Macroeconomics    |
| Diebold & Mariano | 1995 | Predictive Accuracy Comparison Test  |

---

**Document Status**: ✅ Version 1.0 — Ready for Implementation
