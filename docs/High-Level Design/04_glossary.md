# 📚 MERIDIAN FX — Glossary & Definitions

---

## 📖 FINANCIAL TERMS

### Market & Trading

| Term | Definition | Context in Meridian |
|------|------------|---------------------|
| **Directional Accuracy (DA)** | Percentage of predictions where the predicted direction matches the actual direction | Primary model evaluation metric |
| **Edge Ratio** | Net Return / Total Cost; > 2.0 indicates meaningful economic edge | Economic filter gatekeeper |
| **Expected Return** | Mean of the predictive distribution for a 5-day forward log return | Core forecast output |
| **Forecast Horizon** | 5 trading days forward from prediction timestamp | Fixed target definition |
| **Gross Return** | Predicted return before subtracting any costs | Economic filter input |
| **Net Return** | Gross Return - Total Costs (spread + slippage + fees) | Actionability decision metric |
| **Pair** | A currency pair (e.g., USD/JPY, EUR/USD) | Base unit of analysis |
| **Position Sizing Factor** | 0-1 value indicating suggested position size relative to maximum | Optional output in V3+ |
| **Profit Factor** | Gross Profit / Gross Loss; > 1.0 indicates profitable strategy | Strategy evaluation metric |
| **Slippage** | Difference between expected and actual trade execution price | Cost component in economic filter |
| **Spread** | Difference between bid and ask price | Cost component in economic filter |
| **Total Cost** | Spread + Slippage + Commission/Fees | Sum of all trading frictions |

### Macroeconomic Terms

| Term | Definition | Context in Meridian |
|------|------------|---------------------|
| **Accommodative** | Monetary policy stance that supports economic growth (low rates, easing) | Japan regime classification |
| **Growth Regime** | Classification of economic growth phase (strong, moderate, weak) | Macro Agent output |
| **Inflation Regime** | Classification of inflation dynamics (high, normal, low) | Macro Agent output |
| **Policy Divergence** | Difference in monetary policy stance between central banks | RAG Agent key output |
| **Restrictive** | Monetary policy stance that constrains economic growth (high rates, tightening) | US regime classification |
| **Risk-Off** | Market environment characterized by flight to safety, rising volatility | Risk regime classification |
| **Risk-On** | Market environment characterized by risk-seeking, low volatility | Risk regime classification |
| **Regime** | A state of the economy or market defined by specific characteristics | Macro context for signal fusion |
| **Regime Stability Score** | 0-1 measure of how stable the current regime is | Risk assessment output |

---

## 🤖 ML/AI TERMS

### Machine Learning

| Term | Definition | Context in Meridian |
|------|------------|---------------------|
| **Ablation Study** | Systematic removal of components to measure their contribution | Experiment sequence E0→E7 |
| **Calibration** | Transformation of raw model probabilities to statistically meaningful probabilities | Platt Scaling / Isotonic Regression |
| **Calibrated Probability** | Probability transformed to be statistically meaningful and well-calibrated | Forecast Level 1 output |
| **Cross-Validation** | Technique for assessing model generalization by splitting data | Walk-forward backtesting |
| **Drift Detection** | Monitoring for changes in model performance or data distribution | Level 4 Evaluation |
| **Embargoing** | Removing data points around train/test boundaries to prevent leakage | Walk-forward backtesting |
| **Ensemble** | Combination of multiple models to improve predictions | E7 in experiment sequence |
| **Feature** | Input variable used by the model for prediction | Feature engineering output |
| **Feature Store** | Centralized repository of features with versioning | TimescaleDB component |
| **Hyperparameters** | Configuration parameters set before model training | Model Registry metadata |
| **Leakage** | Use of future information in model training | Violates `knowledge_timestamp <= prediction_timestamp` |
| **Monotonic Constraints** | Enforcing economic relationships (e.g., higher spread → higher predicted return) | E2b experiment |
| **PIT (Point-in-Time)** | Data as it would have been known at prediction time | Core data quality requirement |
| **Raw Probability** | Direct model output before calibration | Model output |
| **Reproducibility** | Ability to obtain identical results from same inputs | DVC + Git + MLflow |
| **SHAP** | SHapley Additive exPlanations; method for explaining model predictions | Level 2 output component |
| **Walk-Forward** | Rolling or expanding window backtesting for realistic evaluation | Primary backtesting method |
| **XGBoost** | eXtreme Gradient Boosting; primary ML model | Quant Engine core model |

### RAG (Retrieval-Augmented Generation)

| Term | Definition | Context in Meridian |
|------|------------|---------------------|
| **Chunking** | Splitting documents into smaller pieces for processing | RAG Agent preprocessing |
| **Divergence Score** | Measure of deviation from historical policy stance | RAG Agent output |
| **Embedding** | Vector representation of text for semantic search | RAG Agent retrieval |
| **Hawkish** | Monetary policy stance favoring tighter policy (rate increases) | Fed sentiment classification |
| **Dovish** | Monetary policy stance favoring easier policy (rate cuts) | BoJ sentiment classification |
| **Entity Recognition** | Identifying named entities in text (people, organizations) | RAG Agent NLP |
| **FAISS** | Facebook AI Similarity Search; vector search library | RAG Agent vector store (optional) |
| **Retrieval** | Finding relevant document chunks for a query | RAG Agent retrieval step |
| **Sentence-BERT** | BERT variant for generating sentence embeddings | RAG Agent embedding model (optional) |
| **Sentiment Analysis** | Classification of text sentiment (positive/negative) | RAG Agent NLP |
| **Vector Store** | Database for storing and searching embeddings | RAG Agent storage layer |

---

## 📊 METRICS

### Model Evaluation Metrics (Statistical)

| Metric | Symbol | Formula | Threshold | Purpose |
|--------|--------|---------|-----------|---------|
| **Directional Accuracy** | DA | (1/N) × Σ I(sign(ŷ) = sign(y)) | > 52% | Basic predictive power |
| **AUC** | AUC | Integral of ROC curve | > 0.55 | Ranking ability |
| **Brier Score** | BS | (1/N) × Σ (P_pred - y_real)² | < 0.25 | Probability accuracy |
| **Log Loss** | LL | -(1/N) × Σ [y × log(P_pred) + (1-y) × log(1-P_pred)] | < 0.69 | Penalizes overconfidence |
| **Information Coefficient** | IC | Corr(predicted, actual) | > 0.05 | Predictive correlation |
| **Expected Calibration Error** | ECE | Σ_{b=1}^{B} (n_b/N) × \|accuracy_b - confidence_b\| | < 0.05 | Probability reliability |
| **Calibration Curve** | — | Plot of predicted probability vs observed frequency | Near 45° line | Visual calibration check |

### Strategy Evaluation Metrics (Economic)

| Metric | Symbol | Formula | Threshold | Purpose |
|--------|--------|---------|-----------|---------|
| **Sharpe Ratio** | SR | (E[R_p] - R_f) / σ_p × √252 | > 0.3 | Risk-adjusted return |
| **Sortino Ratio** | SoR | (E[R_p] - R_f) / σ_downside × √252 | > 0.2 | Downside risk focus |
| **Maximum Drawdown** | MDD | max(peak - trough) | < -20% | Worst-case loss |
| **Net Return (annualized)** | R_net | (1 + R_net_total)^(252/N) - 1 | > 0% | Real profitability |
| **Profit Factor** | PF | Gross Profit / Gross Loss | > 1.2 | Win/loss ratio |
| **Turnover** | TO | Total trades / Total capital | — | Cost efficiency |
| **Hit Rate** | HR | (1/N) × Σ I(profit_t > 0) | > 50% | Winning trade rate |

### Output Quality Metrics

| Metric | Definition | Threshold | Where Used |
|--------|------------|-----------|------------|
| **Actionability** | Net Return > Minimum Edge | True/False | Level 1 Forecast |
| **Data Coverage** | Percentage of expected data available | > 95% | Data Quality |
| **Edge Ratio** | Net Return / Total Cost | > 2.0 | Level 1 Forecast |
| **Model Drift Score** | Change in model predictions over time | < 0.3 | Level 4 Evaluation |
| **Regime Stability Score** | Stability of current regime classification | > 0.5 | Level 2 Drivers |
| **Signal Strength** | Weak / Moderate / Strong | Based on probability | Level 1 Forecast |
| **System Performance** | Inference latency | < 200ms | Infrastructure |

---

## 📐 FORMULAS

### Forecast & Calibration

#### 1. Target Definition
```
y_t = log(S_{t+h} / S_t)

Where:
- S_t = exchange rate at time t
- h = forecast horizon (5 trading days)
- y_t = log-return over horizon
```

#### 2. Direction Target
```
D_t = 1 if y_t > 0 else 0

Where:
- D_t = direction indicator (1 = bullish, 0 = bearish)
- y_t = log-return over horizon
```

#### 3. Calibrated Probability
```
P_cal = f(P_raw)

Where:
- P_raw = raw model output (probabilistic)
- f(x) = Platt scaling or isotonic regression transformation
- P_cal = statistically calibrated probability ∈ [0, 1]
```

#### 4. Expected Return
```
E[R] = E[log(S_{t+h} / S_t) | I_t]

Where:
- E[R] = expected return over horizon
- I_t = information available at time t
- h = forecast horizon
```

#### 5. Expected Volatility
```
σ_h = σ_annual × √(h / 252)

Where:
- σ_annual = annualized volatility estimate
- h = forecast horizon in trading days
- σ_h = expected volatility over horizon
```

#### 6. Prediction Interval (95%)
```
PI_95 = [E[R] - 1.96 × σ_h, E[R] + 1.96 × σ_h]

Where:
- E[R] = expected return
- σ_h = expected volatility over horizon
- PI_95 = 95% prediction interval
```

### Economic Filter

#### 7. Gross Return
```
R_gross = E[R]

Where:
- R_gross = expected gross return
- E[R] = expected return over horizon
```

#### 8. Total Cost
```
C_total = Spread + Slippage + Commission

Where:
- Spread = bid-ask spread cost
- Slippage = execution slippage cost
- Commission = trading commission/fee
- C_total = total trading cost
```

#### 9. Net Return
```
R_net = R_gross - C_total

Where:
- R_net = expected net return
- R_gross = expected gross return
- C_total = total trading cost
```

#### 10. Edge Ratio
```
Edge_Ratio = R_net / C_total

Where:
- Edge_Ratio = edge ratio (unitless)
- R_net = expected net return
- C_total = total trading cost
```

#### 11. Actionability Criterion
```
Actionable = True if R_net > MinEdge else False

Where:
- Actionable = trade is economically worthwhile
- R_net = expected net return
- MinEdge = minimum acceptable edge (typically 0.0020)
```

### Evaluation Metrics

#### 12. Directional Accuracy
```
DA = (1/N) × Σ_{i=1}^{N} I(sign(ŷ_i) = sign(y_i))

Where:
- DA = directional accuracy
- ŷ_i = predicted return for observation i
- y_i = actual return for observation i
- I(.) = indicator function
- N = number of observations
```

#### 13. Brier Score
```
BS = (1/N) × Σ_{i=1}^{N} (p_i - y_i)²

Where:
- BS = Brier score
- p_i = predicted probability for observation i
- y_i = actual outcome (0 or 1) for observation i
- N = number of observations
```

#### 14. Log Loss
```
LL = -(1/N) × Σ_{i=1}^{N} [y_i × log(p_i) + (1-y_i) × log(1-p_i)]

Where:
- LL = log loss
- p_i = predicted probability for observation i
- y_i = actual outcome (0 or 1) for observation i
- N = number of observations
```

#### 15. Expected Calibration Error (ECE)
```
ECE = Σ_{b=1}^{B} (n_b / N) × |acc_b - conf_b|

Where:
- ECE = expected calibration error
- B = number of bins
- n_b = number of observations in bin b
- N = total number of observations
- acc_b = actual accuracy in bin b
- conf_b = average predicted confidence in bin b
```

#### 16. Sharpe Ratio (Annualized)
```
SR = (E[R_p] - R_f) / σ_p × √252

Where:
- SR = annualized Sharpe ratio
- E[R_p] = expected portfolio return
- R_f = risk-free rate
- σ_p = standard deviation of portfolio returns
- √252 = annualization factor (trading days)
```

#### 17. Sortino Ratio (Annualized)
```
SoR = (E[R_p] - R_f) / σ_downside × √252

Where:
- SoR = annualized Sortino ratio
- E[R_p] = expected portfolio return
- R_f = risk-free rate
- σ_downside = standard deviation of negative returns
- √252 = annualization factor (trading days)
```

#### 18. Maximum Drawdown
```
MDD = min_{0 ≤ t ≤ T} [min_{0 ≤ s ≤ t} (1 - V_s / V_t)]

Where:
- MDD = maximum drawdown
- V_t = portfolio value at time t
- V_s = portfolio value at time s (peak)
- T = total time period
```

#### 19. Profit Factor
```
PF = Gross_Profit / Gross_Loss

Where:
- PF = profit factor
- Gross_Profit = sum of all profitable trades
- Gross_Loss = sum of all losing trades (absolute value)
```

### Global Intelligence

#### 20. Pair Score
```
Score_pair = Σ_{i=1}^{n} w_i × Signal_i

Where:
- Score_pair = composite score for a currency pair
- Signal_i = individual signal value (normalized to [-1, +1])
- w_i = weight for signal i
- Σ_{i=1}^{n} w_i = 1.0
```

#### 21. Cross-Correlation
```
ρ_{AB} = Corr(R_A, R_B)

Where:
- ρ_{AB} = correlation between returns of pair A and B
- R_A = returns of pair A
- R_B = returns of pair B
```

#### 22. Divergence Score
```
Divergence = Signal_current - Historical_Percentile(Signal)

Where:
- Divergence = divergence score
- Signal_current = current signal value
- Historical_Percentile = percentile of historical signal distribution
```

#### 23. Independence Score
```
Independence = 1 - |Correlation(Signal, Market_Factor)|

Where:
- Independence = independence score ∈ [0, 1]
- Signal = signal being evaluated
- Market_Factor = broad market factor (e.g., USD strength)
```

### RAG Agent

#### 24. Policy Divergence
```
Policy_Divergence = |Sentiment_Fed - Sentiment_BoJ|

Where:
- Policy_Divergence = divergence between central bank stances
- Sentiment_Fed = Fed sentiment score ∈ [0, 1]
- Sentiment_BoJ = BoJ sentiment score ∈ [0, 1]
```

#### 25. Z-Score Normalization (12-month)
```
z_t = (x_t - μ_{t-12:t}) / σ_{t-12:t}

Where:
- z_t = z-score at time t
- x_t = value at time t
- μ_{t-12:t} = mean over past 12 months
- σ_{t-12:t} = standard deviation over past 12 months
```

### Data Quality

#### 26. Data Quality Score
```
DQ = (w_m × Q_m + w_a × Q_a + w_t × Q_t) / (w_m + w_a + w_t)

Where:
- DQ = overall data quality score
- Q_m = quality of market data
- Q_a = quality of macro data
- Q_t = quality of text data
- w_m, w_a, w_t = weights for each data type

Each Q ∈ [0, 1]:
- Q = 1.0 if all features available and current
- Q = 0.7 if some features missing but critical data available
- Q = 0.4 if major features missing
- Q = 0.0 if prediction cannot be made
```

---

## 📋 QUICK REFERENCE CARD

### Key Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Directional Accuracy | > 52% | Above baseline |
| Sharpe Ratio (net) | > 0.3 | Economically significant |
| Calibration Error (ECE) | < 0.05 | Reliable probabilities |
| Edge Ratio | > 2.0 | Cost-justified |
| Maximum Drawdown | < -20% | Risk threshold |
| Profit Factor | > 1.2 | Profitable strategy |
| Data Coverage | > 95% | Sufficient data |
| System Latency | < 200ms | Acceptable response |

### Key Equations Summary

| Concept | Formula |
|---------|---------|
| Target Return | y_t = log(S_{t+h}/S_t) |
| Calibrated Probability | P_cal = f(P_raw) |
| Expected Return | E[R] = E[log(S_{t+h}/S_t) \| I_t] |
| Expected Volatility | σ_h = σ_annual × √(h/252) |
| Net Return | R_net = E[R] - C_total |
| Edge Ratio | Edge = R_net / C_total |
| Actionability | Actionable = R_net > MinEdge |
| Sharpe Ratio | SR = (E[R_p] - R_f) / σ_p × √252 |
| Brier Score | BS = (1/N) × Σ (p_i - y_i)² |
| ECE | ECE = Σ (n_b/N) × \|acc_b - conf_b\| |
| Policy Divergence | Div = \|Sentiment_Fed - Sentiment_BoJ\| |

---

**Meridian FX — Glossary & Definitions v1.0** ✅