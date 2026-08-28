from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from .routers import forecast, drivers, ranking, performance, status, historical

app = FastAPI(
    title="Meridian FX Layer 1 API",
    version="1.0.0",
    description="Layer 1 API serving Meridian FX intelligence"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast.router)
app.include_router(drivers.router)
app.include_router(ranking.router)
app.include_router(performance.router)
app.include_router(status.router)
app.include_router(historical.router)

@app.get("/")
async def root():
    return {"message": "Meridian FX Layer 1 API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
