from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from layer1.routers import ranking, drivers, forecast, performance, status, historical

app = FastAPI(title="Meridian FX API", version="1.0.0")

# Configurar CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:73",
        "http://127.0.0.1:73",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(ranking.router)
app.include_router(drivers.router)
app.include_router(forecast.router)
app.include_router(performance.router)
app.include_router(status.router)
app.include_router(historical.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Meridian FX API is running"}

@app.get("/")
async def root():
    return {"message": "Meridian FX API", "version": "1.0.0"}
from layer1.routers import interpretation
app.include_router(interpretation.router)
from layer1.routers import interpretation
app.include_router(interpretation.router)
