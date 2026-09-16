from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.layer1.routers import ranking, forecast, performance, status, historical, interpretation, price, model_comparison, forecast_dashboard, intelligence, canonical, narrative, divergence

app = FastAPI(title="Meridian FX API", version="1.0.0")

# CORS configuration.
#
# IMPORTANT: do NOT include "*" in allow_origins when
# allow_credentials=True — the CORS spec forbids it, and browsers
# will silently reject every response (which manifests as
# "No 'Access-Control-Allow-Origin' header is present").
#
# List every allowed origin explicitly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        # Production frontend (Cloudflare Pages)
        "https://meridianfx.pages.dev",
        "https://main.meridianfx.pages.dev",
        "https://*.pages.dev",
        # Legacy frontends (kept for compatibility while migrating)
        "https://meridian-fx-frontend.vercel.app",
        "https://meridian-fx-frontend-git-main.vercel.app",
        "https://preset-cost-freehand.ngrok-free.dev",
        "https://*.ngrok-free.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers - CORREGIDO
app.include_router(ranking.router, prefix="/v1/fx", tags=["ranking"])
app.include_router(forecast.router, prefix="/v1/fx", tags=["forecast"])
app.include_router(performance.router, prefix="/v1/fx", tags=["performance"])
app.include_router(status.router, prefix="/v1", tags=["status"])
app.include_router(intelligence.router, prefix="/v1", tags=["intelligence"])
app.include_router(canonical.router, prefix="/v1/canonical", tags=["canonical"])
app.include_router(narrative.router, prefix="/v1/canonical", tags=["narrative"])
app.include_router(historical.router, prefix="/v1/fx", tags=["historical"])
app.include_router(interpretation.router, prefix="/v1/fx", tags=["interpretation"])
app.include_router(price.router, prefix="/v1/fx", tags=["price"])
app.include_router(model_comparison.router, prefix="/v1/fx", tags=["model_comparison"])
app.include_router(forecast_dashboard.router, prefix="/v1/fx", tags=["forecast-dashboard"])
app.include_router(divergence.router, prefix="/v1/fx", tags=["divergence"])

@app.get("/")
async def root():
    return {"message": "Meridian FX API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Meridian FX API is running"}
