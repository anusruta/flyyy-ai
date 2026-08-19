from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db, engine
from app.observability.telemetry import setup_telemetry
from app.services.retention import start_retention_scheduler, stop_retention_scheduler
from app.api import assets, interactions, agent_runs, analytics, governance
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_telemetry(settings.OTEL_SERVICE_NAME, engine)
    await init_db()
    start_retention_scheduler(settings.RETENTION_CHECK_INTERVAL_HOURS)
    yield
    # Shutdown
    stop_retention_scheduler()

app = FastAPI(
    title="FLYYY.AI Governance API",
    description="AI Usage Observability & Governance Platform",
    version="1.0.0",
    redirect_slashes=False,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["interactions"])
app.include_router(agent_runs.router, prefix="/api/agent-runs", tags=["agent-runs"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(governance.router, prefix="/api/governance", tags=["governance"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "flyy-ai-governance"}
