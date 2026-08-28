from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from layer1.routers import ranking, drivers, forecast, performance, status, historical, interpretation

app = FastAPI(title="Meridian FX API", version="1.0.0")

# Configurar CORS - solo el puerto que usamos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ranking.router)
app.include_router(drivers.router)
app.include_router(forecast.router)
app.include_router(performance.router)
app.include_router(status.router)
app.include_router(historical.router)
app.include_router(interpretation.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Meridian FX API is running"}

@app.get("/")
async def root():
    return {"message": "Meridian FX API", "version": "1.0.0"}
