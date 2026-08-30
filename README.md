## 📄 README.md ACTUALIZADO (EN INGLÉS)

Aquí tienes el `README.md` completo y actualizado para Meridian FX v2.3.0:

```bash
cd ~/repo_lab/MeridianFX

cat > README.md << 'EOF'
# Meridian FX

**Financial Intelligence & Decision Support System**

**A Stratus Intelligence Project**

Developed by **Daniel Canedo, MSc in Economics**

---

## Overview

Meridian FX is a quantitative foreign-exchange intelligence platform that transforms market data, macroeconomic indicators, and textual signals into **actionable, traceable, explainable, and measurable financial intelligence**.

It does not merely produce predictions. It produces structured decision outputs with full governance — every forecast is decomposed into economic drivers (SHAP), macro regime context, RAG-based central-bank sentiment, and explicit invalidation conditions.

**Current scope:** 9 currency pairs (USD/JPY, EUR/USD, GBP/USD, USD/CNY, USD/MXN, USD/BRL, USD/ARS, USD/BOB, USD/CHF) with 30/60/90-day forecast horizons.

---

## What Meridian Answers

| Question | Module |
| -------- | ------ |
| What is happening in the market? | Global Overview |
| What does Meridian expect? | Forecast Dashboard |
| Why? | Drivers & Explanation |
| Is it worth acting? | Economic Filter |
| What could invalidate the signal? | Signal Validity |
| How good has Meridian been? | Performance Dashboard |
| Which model performs best? | Model Comparison |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              MERIDIAN FX                                    │
│                   Financial Intelligence System                             │
│                                                                              │
│   ┌───────────────┐   delivery contracts (Layer 1 §7)   ┌─────────────────┐ │
│   │   LAYER 1     │ ──────────────────────────────────▶ │   FRONTEND      │ │
│   │ DELIVERY API  │  /v1/fx/{pair}/forecast|drivers     │   Dashboard     │ │
│   │  (FastAPI)    │  /v1/fx/ranking · performance       │   React + TS    │ │
│   └───────┬───────┘  /v1/fx/interpretation · macro      │   Fan Chart     │ │
│           │         /v1/fx/{pair}/model-comparison      │   SignalIQ      │ │
│           │  imports / uses layer2 engine + src decision │   LLM Context   │ │
│   ┌───────▼──────────────┐         ┌────────────────────┐ ┌───────────────┐ │
│   │ LAYER 2  LIVE ENGINE │         │  LAYER 3           │ │  LAYER 4      │ │
│   │ layer2/: XGBoost ·    │ ◀───── │ MODEL / SHAP /     │ │ DATA QUALITY  │ │
│   │ SHAP · data providers │ artifact│ RAG / narrative    │ │ FRESHNESS /   │ │
│   │ Yahoo→Alpha→Twelve ·  │ + L4   │ (external)         │ │ DRIFT (ext.)  │ │
│   │ FRED macro · ranking  │ streams│                    │ │               │ │
│   └──────────┬────────────┘        └────────────────────┘ └───────────────┘ │
│              │  + src/meridian_fx/decision/ (contract-governed engine)       │
│                                                                              │
│   Deployment target: Render (FastAPI) + Neon (PostgreSQL)                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Role | Technology |
| ----- | ---- | ---------- |
| **Layer 1** — Delivery API | REST endpoints, response contracts | FastAPI, Uvicorn, Pydantic |
| **Layer 2** — Decision Engine | 8-stage deterministic pipeline | Python, XGBoost, scikit-learn, SHAP |
| **Layer 3** — Research Layer | Model training, walk-forward, Research Gate | Python, ARIMA, Elastic Net, Ensemble |
| **Layer 4** — Data Layer | PIT validation, Lineage, Versioned Config | Python, PIT Validator |
| **Frontend** — Dashboard | Contract-driven presentational UI | React 18, TypeScript, Vite, Tailwind |

---

## Tech Stack

### Backend

| Component | Technology |
| --------- | ---------- |
| Language | Python 3.12 |
| API framework | FastAPI + Uvicorn |
| Data validation | Pydantic 2 |
| ML models | XGBoost 3.4, Logistic, ARIMA, scikit-learn |
| Explainability | SHAP |
| Data processing | pandas, numpy, pandas_ta |
| Data sources | Yahoo Finance, Alpha Vantage, Twelve Data, FRED |
| LLM Integration | Groq, GLM, Gemini (with fallback) |
| Testing | pytest (99 tests) |

### Frontend

| Component | Technology |
| --------- | ---------- |
| UI framework | React 18 + TypeScript 5 |
| Build tool | Vite 5 |
| Styling | Tailwind CSS 3 |
| Data fetching | TanStack Query 5 + Axios |
| Routing | react-router-dom 6 |
| Charts | Recharts 2 |
| Dates | date-fns 3 |
| Testing | Vitest + Testing Library (55 tests) |

---

## Key Features

### 📊 Global Intelligence
- **SignalIQ-style price chart** with gradient area and interactive hover
- **Real-time spot prices** from Yahoo Finance
- **30/60/90-day XGBoost forecasts** with 95% confidence intervals
- **Opportunity ranking** with edge ratio and actionable status
- **LLM-powered economic interpretation** of market context

### 📈 Probabilistic Forecast
- **Institutional-style Fan Chart** with P10, P25, P50, P75, P90 quantiles
- **Historical + forecast integration** with "NOW" separator
- **Professional blue palette** with gradient bands
- **Detailed tooltip** with confidence intervals

### 🔍 Drivers & Explanation
- **SHAP values** for model explainability
- **Macro regime classification** (Risk-On/Off, Policy, Growth, Inflation)
- **RAG-based central bank sentiment** (Fed, BoJ)
- **Executive narrative** and risk analysis

### 🧠 Model Comparison
- **XGBoost vs Logistic vs Ensemble** walk-forward evaluation
- **Sharpe ratio, Profit Factor, DA, AUC** metrics
- **Research Gate** validation with configurable thresholds
- **Transparent model selection** based on OOS performance

### 📉 Data Quality (PIT)
- **7 PIT invariants** (PIT-1 to PIT-7)
- **Adversarial datasets** A-D for validation
- **Lineage tracking** for auditability
- **Versioned configuration** (YAML-based)

---

## Project Structure

```
MeridianFX/
├── docs/                          Frozen specifications, prompts, contract governance
├── layer1/                        FastAPI delivery API (routers, models, LLM)
├── layer2/                        Live engine (data, features, models, explainers, macro)
├── layer3/                        Research Layer (ARIMA, Elastic Net, Ensemble, RAG)
├── layer4/                        Data Layer (PIT validation, Lineage, Config)
├── src/meridian_fx/decision/      Contract-governed Decision Engine (99 tests)
├── frontend/                      React + TypeScript dashboard
│   ├── src/
│   │   ├── components/            Presentational components
│   │   ├── hooks/                 Data-fetching hooks
│   │   ├── pages/                 Page composition
│   │   ├── services/              API client + adapters
│   │   ├── types/                 Contract types + gaps
│   │   └── utils/                 Formatting utilities
│   └── ...
├── models/                        Trained .pkl models + registry
├── cache/                         Runtime forecast + macro caches
├── train_models.py                XGBoost training script
├── pyproject.toml                 Backend project metadata
├── requirements.txt               Backend dependencies
├── README.md                      This file
└── architecture.md                System architecture document
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/danacioDS/MeridianFX.git
cd MeridianFX

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Start the API server
uvicorn layer1.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run typecheck
npm run typecheck

# Run tests
npm test

# Build for production
npm run build
```

### Environment Variables (Frontend)

Copy `.env.example` to `.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=dev_placeholder_key_only
VITE_POLLING_INTERVAL=60000
VITE_ENVIRONMENT=development
```

> **Security:** Never commit real API keys. Use secure authentication for production.

### Environment Variables (Backend)

```bash
# Required for macro data
FRED_API_KEY=your_fred_api_key

# Optional LLM providers
GROQ_API_KEY=your_groq_api_key
GLM_API_KEY=your_glm_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## Testing

| Suite | Command | Coverage |
| ----- | ------- | -------- |
| Backend | `python -m pytest` | 99 tests |
| Frontend typecheck | `cd frontend && npm run typecheck` | TypeScript clean |
| Frontend tests | `cd frontend && npm test` | 55 tests |
| Frontend build | `cd frontend && npm run build` | Production build |

---

## Deployment

### Render.com (Recommended)

1. Push repository to GitHub
2. Connect to Render.com
3. Configure services:

**Backend:**
```yaml
type: web
name: meridian-fx-backend
runtime: python
buildCommand: pip install -r requirements.txt
startCommand: uvicorn layer1.main:app --host 0.0.0.0 --port 10000
```

**Frontend:**
```yaml
type: web
name: meridian-fx-frontend
runtime: static
buildCommand: npm install && npm run build
staticPublishPath: ./frontend/dist
```

### Local Production Build

```bash
# Backend
cd ~/repo_lab/MeridianFX
source venv/bin/activate
uvicorn layer1.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npx serve -s dist -p 5174
```

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/fx/ranking` | GET | Opportunity ranking (9 pairs) |
| `/v1/fx/{pair}/forecast` | GET | Point forecast (XGBoost) |
| `/v1/fx/{pair}/forecast-dashboard` | GET | Full dashboard data (trends, volatility, forecasts) |
| `/v1/fx/{pair}/drivers` | GET | SHAP drivers + macro + RAG |
| `/v1/fx/{pair}/performance` | GET | Model performance metrics |
| `/v1/fx/interpretation` | GET | LLM-powered economic interpretation |
| `/v1/fx/{pair}/model-comparison` | GET | XGBoost vs Logistic vs Ensemble |
| `/v1/status` | GET | System status |
| `/health` | GET | Health check |

---

## Contract Governance

The frontend is **contract-driven**. All domain data comes from Layer 1 v5.1 contracts.

- **No derivation:** the frontend does NOT calculate, infer, rank, or derive values
- **Transport only:** backend responses are consumed verbatim
- **No fallback:** unsupported elements render `NOT_AVAILABLE`
- **Nullability preserved:** `null` is never replaced with defaults

| Artifact | Role |
| -------- | ---- |
| `CONTRACT_TRACEABILITY.md` | 73-row element → contract matrix (61 verified) |
| `CONTRACT_GAPS.md` | 16 gaps documented |
| `FRONTEND_CONTRACT_FREEZE.md` | FREEZE WITH OPTIONAL GAPS |

---

## License

© 2026 Stratus Intelligence. All rights reserved.

---

<p align="center">
  <strong>MERIDIAN FX</strong><br>
  Financial Intelligence System<br><br>
  <strong>STRATUS INTELLIGENCE</strong>
</p>
EOF
```

---

## 🚀 VERIFICAR

```bash
cd ~/repo_lab/MeridianFX

# Verificar que el README se creó correctamente
cat README.md | head -80

# Añadir a git
git add README.md
git commit -m "docs: README.md actualizado v2.3.0"
```

---

**🎯 ¡README.md actualizado y listo para la entrevista!** 🚀


## Back End 

cd ~/repo_lab/MeridianFX

# 1. Matar todos los procesos de uvicorn
pkill -9 -f uvicorn || true

# 2. Liberar el puerto 8000
sudo fuser -k 8000/tcp 2>/dev/null || true

# 3. Esperar a que el puerto se libere
sleep 2

# 4. Verificar que el puerto está libre
ss -ltnp | grep ':8000' || echo "✅ Puerto 8000 libre"

# 5. Iniciar backend
source venv/bin/activate
uvicorn layer1.main:app --reload --host 0.0.0.0 --port 8000

## Frontend 

cd ~/repo_lab/MeridianFX/frontend

# 1. Verificar que el backend está corriendo (en otra terminal)
curl -s http://localhost:8000/health

# 2. Iniciar el frontend en modo desarrollo
npm run dev