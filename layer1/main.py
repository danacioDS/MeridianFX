from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from layer1.routers import ranking, drivers, forecast, performance, status, historical, interpretation, price, model_comparison, forecast_dashboard

app = FastAPI(title="Meridian FX API", version="1.0.0")

# Configurar CORS - ACTUALIZADO CON DOMINIO DE CLOUDFLARE
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
        # 👇 NUEVOS DOMINIOS DE CLOUDFLARE
        "https://main.meridianfx.pages.dev",
        "https://meridianfx.pages.dev",
        "https://*.pages.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar todos los routers
app.include_router(ranking.router)
app.include_router(drivers.router)
app.include_router(forecast.router)
app.include_router(performance.router)
app.include_router(status.router)
app.include_router(historical.router)
app.include_router(interpretation.router)
app.include_router(price.router)
app.include_router(model_comparison.router)
app.include_router(forecast_dashboard.router)

@app.get("/")
async def root():
    return {"message": "Meridian FX API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Meridian FX API is running"}
