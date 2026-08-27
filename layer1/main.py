from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Importar routers explícitamente
from layer1.routers.forecast import router as forecast_router
from layer1.routers.drivers import router as drivers_router
from layer1.routers.ranking import router as ranking_router
from layer1.routers.performance import router as performance_router
from layer1.routers.status import router as status_router

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

# Incluir routers
app.include_router(forecast_router)
app.include_router(drivers_router)
app.include_router(ranking_router)
app.include_router(performance_router)
app.include_router(status_router)

@app.get("/")
async def root():
    return {"message": "Meridian FX Layer 1 API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
