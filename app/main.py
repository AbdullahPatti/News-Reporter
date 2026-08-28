from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.routers import auth, dashboard
from app.services.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown (optional)
    # scheduler.shutdown()

app = FastAPI(
    title="News Reporter",
    description="AI News Aggregator Agent",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }