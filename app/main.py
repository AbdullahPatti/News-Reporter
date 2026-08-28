from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.config import settings
from app.routers import auth, dashboard
from app.services.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield


app = FastAPI(
    title="Daily Digest",
    description="AI News Aggregator Agent",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(dashboard.router)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }