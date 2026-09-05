from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.layer1.routers import ranking, drivers, forecast, performance, status, historical, interpretation, price, model_comparison, forecast_dashboard

app = FastAPI(title="Meridian FX API", version="1.0.0")

# Configurar CORS - ACTUALIZADO CON DOMINIOS DE CLOUDFLARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://meridianfx.onrender.com",
        "https://meridianfx-1.onrender.com",
        "https://meridian-fx-frontend.vercel.app",
        "https://meridian-fx-frontend-git-main.vercel.app",
        "https://main.meridianfx.pages.dev",
        "https://meridianfx.pages.dev",
        "https://*.pages.dev",
        "https://preset-cost-freehand.ngrok-free.dev",
        "https://*.ngrok-free.dev",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers - CORREGIDO
app.include_router(ranking.router, prefix="/v1/fx", tags=["ranking"])
app.include_router(drivers.router, prefix="/v1/fx", tags=["drivers"])
app.include_router(forecast.router, prefix="/v1/fx", tags=["forecast"])
app.include_router(performance.router, prefix="/v1/fx", tags=["performance"])
app.include_router(status.router, prefix="/v1", tags=["status"])
app.include_router(historical.router, prefix="/v1/fx", tags=["historical"])
app.include_router(interpretation.router, prefix="/v1/fx", tags=["interpretation"])
app.include_router(price.router, prefix="/v1/fx", tags=["price"])
app.include_router(model_comparison.router, prefix="/v1/fx", tags=["model_comparison"])
app.include_router(forecast_dashboard.router, prefix="/v1/fx", tags=["forecast-dashboard"])

@app.get("/")
async def root():
    return {"message": "Meridian FX API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Meridian FX API is running"}
