# Meridian FX — README completo

**Financial Intelligence & Decision Support System**
**A Stratus Intelligence Project**
Developed by **Daniel Canedo, MSc in Economics**

**Versión actual: v2.7** (honesty & hardening release · tag `v2.7` pendiente)

---

## Overview

Meridian FX es una plataforma cuantitativa de inteligencia FX que transforma datos de mercado, indicadores macroeconómicos y señales textuales en **inteligencia financiera accionable, trazable, explicable y medible**.

No produce únicamente predicciones. Produce **salidas de decisión estructuradas con gobernanza completa**: cada forecast se descompone en drivers económicos (SHAP), contexto de régimen macro, sentimiento de bancos centrales basado en keywords, y condiciones explícitas de invalidación.

**Scope actual:** 9 pares FX (USD/JPY, EUR/USD, GBP/USD, USD/CNY, USD/MXN, USD/BRL, USD/ARS, USD/BOB, USD/CHF) con horizonte canónico de 5 días (ver *Horizon semantics* en Current Limitations).

---

## What Meridian Answers

| Pregunta | Módulo |
|----------|--------|
| ¿Qué está pasando en el mercado? | Global Overview |
| ¿Qué espera Meridian? | Forecast Dashboard |
| ¿Por qué? | Drivers & Explanation |
| ¿Vale la pena actuar? | Economic Filter |
| ¿Qué podría invalidar la señal? | Signal Validity |
| ¿Qué tan bueno ha sido Meridian? | Performance Dashboard |
| ¿Qué modelo rinde mejor? | Model Comparison |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              MERIDIAN FX                                     │
│                   Financial Intelligence System                              │
│                                                                              │
│   ┌───────────────┐   delivery contracts (Layer 1 §7)   ┌─────────────────┐ │
│   │   LAYER 1     │ ──────────────────────────────────▶ │   FRONTEND      │ │
│   │ DELIVERY API  │  /v1/fx/ranking                     │   Dashboard     │ │
│   │  (FastAPI)    │  /v1/fx/{pair}/price|forecast-dashboard    React + TS  │ │
│   │  12 routers   │  /v1/market-intelligence             │  6 pages        │ │
│   └───────┬───────┘  /v1/canonical/{pair}/decision|risk  │  TanStack Query │ │
│           │                                              │  Recharts       │ │
│           │  uses: layer2 engine + src decision          │                 │ │
│   ┌───────▼──────────────┐   ┌────────────────────┐   ┌───────────────────┐ │
│   │ LAYER 2  LIVE ENGINE │   │  LAYER 3           │   │  LAYER 4          │ │
│   │ Logistic_24 + XGBoost│◀─ │ RESEARCH           │   │ DATA QUALITY      │ │
│   │ SHAP · PIT policy_diff│  │ walkforward ·      │   │ PITValidator      │ │
│   │ Yahoo→Alpha→Twelve    │  │ benchmarks · RAG   │   │ (tests only)      │ │
│   │ FRED macro · ranking  │  │ research_gate      │   │                   │ │
│   └──────────┬────────────┘  └────────────────────┘   └───────────────────┘ │
│              │                                                                │
│   + src/meridian_fx/decision/ (contract-governed engine: pipeline + Risk v2.3)│
│                                                                              │
│   Deployment: Render (FastAPI) + Cloudflare Pages / Vercel (React)           │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Rol | Tecnología |
|-------|-----|------------|
| **Layer 1** — Delivery API | REST endpoints, response contracts | FastAPI, Uvicorn, Pydantic |
| **Layer 2** — Live Engine | Logistic_24 + XGBoost + SHAP + PIT | Python, scikit-learn, XGBoost, SHAP |
| **Layer 3** — Research | Walk-forward, benchmarks, keyword sentiment | Python, ARIMA, Elastic Net, Ensemble |
| **Layer 4** — Data Quality | PIT validation, Lineage, Config | Python, PITValidator |
| **Frontend** — Dashboard | Contract-driven presentational UI | React 18, TypeScript 5, Vite 5, Tailwind 3 |

---

## Tech Stack

### Backend

| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python 3.12 |
| API framework | FastAPI + Uvicorn |
| Validación | Pydantic 2 |
| Modelos ML | Logistic_24 (canonical), XGBoost, ARIMA, scikit-learn |
| Explicabilidad | SHAP |
| Procesamiento | pandas, numpy, pandas_ta |
| Fuentes de datos | Yahoo Finance, Alpha Vantage, Twelve Data, FRED |
| Testing | pytest (**132 tests**) |

### Frontend

| Componente | Tecnología |
|------------|------------|
| UI framework | React 18 + TypeScript 5 |
| Build tool | Vite 5 |
| Styling | Tailwind CSS 3 |
| Data fetching | TanStack Query 5 + Axios |
| Routing | react-router-dom 6 |
| Charts | Recharts 2 |
| Dates | date-fns 3 |
| Testing | Vitest + Testing Library (**56 tests**) |

---

## Key Features

### 📊 Global Intelligence
- Market Intelligence hero (system-wide status)
- SignalIQ-style price chart con hover interactivo
- Forecasts Logistic_24 (target 5d) con intervalos de confianza al 95%
- Opportunity ranking con edge ratio y actionable status
- Leading signals (top 5 oportunidades)

### 📈 Market
- Precio spot + chart histórico OHLCV
- Trend cards (1m / 3m / 6m / 1y)
- Forecast con horizonte 5d (el parámetro `horizon_days` escala volatilidad)

### 🌐 Macro
- Macro regime (4 ejes: risk / policy / growth / inflation)
- Policy differentials (tasas base/quote)
- Data availability status

### ⚠️ Risk
- **RiskEngine v2.3.0** (score 0-100, level LOW/MODERATE/HIGH/EXTREME)
- 5 risk drivers con explanation
- Context summary

### 🎯 Decision
- Direction + confidence + actionable + validity
- **Economic Breakdown** (gross, carry, cost, net, edge, required min)
- **Hard Gates** (7 filters + thresholds)
- **Quality Metrics** (score + 5 components)
- **Signal Fusion** (quant/macro/sentiment weights)
- Position sizing + multipliers
- SHAP drivers (top 10)

### 📖 About
- Project story
- Academic foundation
- Author

---

## Project Structure

```
MeridianFX/
├── docs/                          Frozen specs, governance, DEUDA_TECNICA_v2.5.md
├── backend/                       Python backend
│   ├── layer1/                    FastAPI delivery API (12 routers)
│   ├── layer2/                    Live engine (Logistic_24 + XGBoost + SHAP + PIT)
│   ├── layer3/                    Research layer (walkforward, benchmarks, RAG)
│   ├── layer4/                    Data quality (PIT validator)
│   ├── src/meridian_fx/decision/  Contract-governed Decision Engine (132 tests)
│   ├── models/                    Tracked .pkl + registry.json + canonical/
│   └── tests/                     Backend pytest suite (14 files)
├── frontend/                      React + TypeScript dashboard
│   ├── src/
│   │   ├── components/            Presentational components
│   │   ├── hooks/                 Data-fetching hooks (10 modules)
│   │   ├── pages/                 6 canonical pages
│   │   ├── services/              API client + adapters
│   │   ├── types/                 Contract types + gaps
│   │   └── utils/                 Formatting utilities
│   └── public/fonts/              Self-hosted fonts (Inter, IBM Plex Mono, Instrument Serif)
├── models/canonical/              Logistic_24 canonical models (.joblib)
├── Dockerfile                     Render container
├── render.yaml                    Render blueprint
├── requirements.txt               Backend dependencies
└── README.md                      This file
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
pip install -r backend/requirements.txt

# Run tests (from repo root)
PYTHONPATH=backend python -m pytest backend/tests
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run typecheck
npm run typecheck

# Run tests
npm test -- --run

# Build for production
npm run build
```

### Environment Variables

**Backend** (`.env`):
```bash
FRED_API_KEY=your_fred_api_key
GROQ_API_KEY=your_groq_api_key        # optional
ALPHA_VANTAGE_API_KEY=your_key        # optional
TWELVE_DATA_API_KEY=your_key          # optional
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_URL=http://localhost:8000
```

**Frontend production** (`frontend/.env.production`):
```bash
VITE_API_URL=https://meridianfx.onrender.com
```

---

## Testing

| Suite | Command | Cobertura |
|-------|---------|-----------|
| Backend | `PYTHONPATH=backend python -m pytest backend/tests` | **132 tests** |
| Frontend typecheck | `cd frontend && npm run typecheck` | TypeScript clean |
| Frontend tests | `cd frontend && npm test -- --run` | **56 tests** |
| Frontend build | `cd frontend && npm run build` | ~1,006 modules |

---

## Endpoints

| Endpoint | Method | Descripción |
|----------|--------|-------------|
| `/v1/status` | GET | System status (StatusEngine) |
| `/v1/market-intelligence` | GET | English narrative synthesis |
| `/v1/fx/ranking` | GET | Opportunity ranking (legacy registry; 1 pair active post-gate) |
| `/v1/fx/{base}/{quote}/forecast` | GET | Point forecast (Logistic_24) |
| `/v1/fx/{pair}/forecast-dashboard` | GET | Full dashboard (trends, volatility, forecasts) |
| `/v1/fx/{pair}/price` | GET | Spot + historical OHLCV |
| `/v1/fx/{pair}/historical` | GET | Historical data |
| `/v1/fx/{base}/{quote}/drivers` | GET | SHAP drivers + macro |
| `/v1/fx/performance/{pair}` | GET | Model performance metrics |
| `/v1/fx/interpretation` | GET | Economic interpretation |
| `/v1/fx/{pair}/model-comparison` | GET | XGBoost vs Logistic walk-forward |
| `/v1/canonical/{pair}/decision` | GET | Contract-governed decision |
| `/v1/canonical/{pair}/risk` | GET | RiskEngine v2.3.0 assessment |
| `/health` | GET | Health check |

---

## Contract Governance

El frontend es **contract-driven**. Todos los datos de dominio vienen de los contratos Layer 1 v5.1.

- **No derivation:** el frontend NO calcula, infiere, rankea ni deriva valores
- **Transport only:** las respuestas del backend se consumen verbatim
- **No fallback:** los elementos no soportados renderizan `NOT_AVAILABLE`
- **Nullability preserved:** `null` nunca se reemplaza con defaults

| Artifact | Rol |
|----------|-----|
| `docs/DEUDA_TECNICA_v2.5.md` | Engineering debt baseline para v2.5 |
| `docs/Contract/CONTRACT_TRACEABILITY.md` | Element → contract matrix |
| `docs/Contract/CONTRACT_GAPS.md` | Gaps documentados |
| `docs/Contract/FRONTEND_CONTRACT_FREEZE.md` | Freeze artifacts |

---

## Versioning

| Versión | Fecha | Highlights |
|---------|-------|------------|
| v2.0.x | Aug 2026 | Frontend inicial |
| v2.1 | Aug 2026 | Macro semantics |
| v2.2 | Aug 2026 | Dynamic forecast + configurable thresholds |
| v2.3 | Aug 2026 | Risk Assessment Engine v2.3.0 |
| v2.4 | Sep 2026 | Frontend rebuild (6 canonical pages) |
| v2.5 | Sep 2026 | Engineering baseline + 6/6 page audit |
| **v2.5.1** | **Sep 2026** | **Repo cleanup + model normalization** |
| **v2.7** | **Sep 2026** | **Registry promotion gate, stub→honest renames, 5d horizon semantics, LLM narrative + provenance, 9-pair universe fix, Docker models/ fix, UI honesty pass** |

---


---

## Current Limitations (v2.7)

This section documents the known gaps between the product's marketing and
the current state of the code. It exists to make the project's boundaries
explicit rather than implicit.

### Data quality governance

- **`StubDataQualityRegistry`, `StubFreshnessRegistry`, `StubDriftRegistry`**
  return fixed placeholder values (`0.90`, `3.0`, `0.05`).
  The UI labels them with a **⚠ STUB badge** (QualityMetrics component);
  they are **not measurements** and must not be read as governance.
- Only **VIX** (`RealFeatureStore`) and **macro data** (FRED, when the API
  key is present) come from real sources in the canonical pipeline.

### Model registry and promotion

- **`models/registry.json`** contains legacy XGBoost models used only by
  the `/v1/fx/ranking` endpoint (RankingEngine). It is **not** the source
  of truth for the canonical decision pipeline.
- The canonical decision pipeline (`/v1/canonical/{pair}/decision`) uses
  **Logistic_24 models** from `models/canonical/*.joblib`. These models
  are **not tracked in `registry.json`** and their AUCs have not been
  measured with the same methodology.
- A promotion gate (`scripts/audit_registry.py`, `scripts/apply_gate.py`)
  now enforces `auc >= 0.52` and `n_samples >= 300` for legacy registry
  models. After applying the gate, **only USD/CHF remains active** in the
  registry; the other 9 models are `CANDIDATE` and are not served.
- **`train_models.py` is deprecated** (see its docstring).

### Horizon semantics

- **The Logistic_24 models are trained on a 5-day forward target.**
  The API's `horizon_days` parameter is **not a per-horizon model**;
  it is a volatility-scaling factor:
  `expected_return = (2P - 1) × volatility × sqrt(horizon_days / 365)`.
- Multi-horizon models (5d, 30d, 90d) are planned for v3.0.

### LLM chain

- The LLM chain (`backend/layer1/llm/`) is **only used by the narrative
  layer** introduced in v2.5. Other endpoints use rule-based logic.
- The narrative layer uses **Groq (`qwen/qwen3.8-27b`)** with a
  deterministic template fallback. Fallback narratives are **not
  persisted** so the next request retries the LLM.

### Sentiment analysis

- `backend/layer3/rag/agents.py` is a **keyword-based sentiment scorer**,
  not Retrieval-Augmented Generation. It uses a dictionary of
  hawkish/dovish terms with no embeddings, vector store, or retrieval.
  The class was renamed to `CentralBankSentimentEngine`; the directory
  name is retained for now.

### CI/CD

- No CI/CD is configured. Typecheck, tests, and quality gates are run
  manually.


## License

© 2026 Stratus Intelligence. All rights reserved.

---

<p align="center">
  <strong>MERIDIAN FX</strong><br>
  Financial Intelligence System<br><br>
  <strong>STRATUS INTELLIGENCE</strong>
</p>

---

# 🚀 Quickstart — Levantar el proyecto

## Arranque completo (backend + frontend)

```bash
# Ir al repo
cd ~/repo_lab/MeridianFX

# Matar procesos previos
pkill -f "uvicorn backend.layer1.main" 2>/dev/null
pkill -f "vite preview" 2>/dev/null
sleep 2

# ─── Backend ───
echo "→ Levantando backend (:8000)..."
PYTHONPATH=.:backend:backend/src setsid uvicorn backend.layer1.main:app \
  --host 0.0.0.0 --port 8000 \
  > /tmp/meridianfx_backend.log 2>&1 < /dev/null &
sleep 8

# ─── Frontend (preview producción) ───
echo "→ Levantando frontend (:5173)..."
cd frontend
npm run build 2>&1 | tail -3
setsid npx vite preview --host 0.0.0.0 --port 5173 \
  > /tmp/meridianfx_frontend.log 2>&1 < /dev/null &
sleep 4

# ─── Verificación ───
cd ~/repo_lab/MeridianFX
echo
echo "════════════════════════════════════════════════════════════════"
echo "Health check"
echo "════════════════════════════════════════════════════════════════"
curl -s -o /dev/null -w "Backend  :8000 → HTTP %{http_code}\n" "http://localhost:8000/v1/status"
curl -s -o /dev/null -w "Frontend :5173 → HTTP %{http_code}\n" "http://localhost:5173/"
echo
echo "Abre: http://localhost:5173/"
```

## Solo backend (para desarrollo de API)

```bash
cd ~/repo_lab/MeridianFX

pkill -f "uvicorn backend.layer1.main" 2>/dev/null
sleep 2

PYTHONPATH=.:backend:backend/src uvicorn backend.layer1.main:app \
  --reload --host 0.0.0.0 --port 8000
```

**Con `--reload`** el backend se reinicia automáticamente al tocar archivos Python.

**Sin `--reload`** (más estable, recomendado para trabajo en frontend):

```bash
PYTHONPATH=.:backend:backend/src uvicorn backend.layer1.main:app \
  --host 0.0.0.0 --port 8000
```

## Solo frontend (dev con hot reload)

```bash
cd ~/repo_lab/MeridianFX/frontend

# Verificar que el backend responde
curl -s http://localhost:8000/v1/status

# Instalar dependencias (si es la primera vez)
npm install

# Dev server con hot reload (puerto 5174)
npm run dev
```

**Acceso**: `http://localhost:5174/`

## Frontend (preview de producción)

```bash
cd ~/repo_lab/MeridianFX/frontend

# Build
npm run build

# Preview (sirve dist/, puerto 5173)
npx vite preview --host 0.0.0.0 --port 5173
```

**Acceso**: `http://localhost:5173/`

## Detener servicios

```bash
# Detener backend
pkill -f "uvicorn backend.layer1.main"

# Detener frontend
pkill -f "vite preview"
pkill -f "vite dev"

# O todo junto
pkill -f "uvicorn|vite"
```

## Ver logs

```bash
# Backend
tail -f /tmp/meridianfx_backend.log

# Frontend
tail -f /tmp/meridianfx_frontend.log
```

## Liberar puertos si están ocupados

```bash
# Puerto 8000 (backend)
sudo fuser -k 8000/tcp 2>/dev/null

# Puerto 5173 (frontend preview)
sudo fuser -k 5173/tcp 2>/dev/null

# Puerto 5174 (frontend dev)
sudo fuser -k 5174/tcp 2>/dev/null
```

## Scripts de atajo (opcionales)

Crea `~/repo_lab/MeridianFX/start.sh`:


## BACKEND

# ¿Qué está corriendo en 5173?
curl -s -o /dev/null -w "Frontend :5173 → HTTP %{http_code}\n" http://localhost:5173/

# ¿Y el backend?
curl -s -o /dev/null -w "Backend :8000 → HTTP %{http_code}\n" http://localhost:8000/v1/status

# ¿Quién ocupa los puertos?
sudo lsof -i :5173 -i :8000 2>/dev/null | head -10

## FRONTEND

cd ~/repo_lab/MeridianFX/frontend
npx vite preview --host 0.0.0.0 --port 5173

**Uso**:
```bash
~/repo_lab/MeridianFX/start.sh   # arrancar todo
~/repo_lab/MeridianFX/stop.sh    # detener todo
```