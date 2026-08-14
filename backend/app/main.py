import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine, SessionLocal
from app.api.agent import router as agent_router
from app.services.computer_service import purge_expired_metric_history
from app.api.maintenance import router as maintenance_router
logger = logging.getLogger("app.cleanup")


async def _metric_history_cleanup_loop() -> None:
    """
    Runs for the lifetime of the app. Every
    METRIC_HISTORY_CLEANUP_INTERVAL_HOURS, deletes metrics_history
    rows older than METRIC_HISTORY_RETENTION_DAYS so the table stays
    a fixed-size rolling window instead of growing indefinitely.
    """
    interval_seconds = settings.METRIC_HISTORY_CLEANUP_INTERVAL_HOURS * 3600

    while True:
        try:
            db = SessionLocal()
            try:
                deleted = purge_expired_metric_history(
                    db, settings.METRIC_HISTORY_RETENTION_DAYS
                )
                if deleted:
                    logger.info(
                        "metrics_history cleanup: removed %d row(s) older than %d days",
                        deleted,
                        settings.METRIC_HISTORY_RETENTION_DAYS,
                    )
            finally:
                db.close()
        except Exception:
            logger.exception("metrics_history cleanup failed")

        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(_metric_history_cleanup_loop())
    yield
    cleanup_task.cancel()


app = FastAPI(
    title="Lab Monitoring System",
    description="Lab PC monitoring and preventive maintenance system",
    version="1.0.0",
    lifespan=lifespan,
)


# Agent routes
app.include_router(agent_router)
# Maintenance route
app.include_router(maintenance_router)

@app.get("/")
def root():
    return {
        "message": "Lab Monitoring System API is running"
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }