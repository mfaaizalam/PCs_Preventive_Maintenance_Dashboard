import asyncio
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine, SessionLocal
from app.api.agent import router as agent_router
from app.api.maintenance import router as maintenance_router
from app.api.computers import router as computers_router
from app.api.ws import router as ws_router
from app.services.computer_service import mark_stale_computers_offline
from app.ws_manager import manager


logger = logging.getLogger("app.cleanup")


async def _offline_sweep_loop():
    """Runs forever in the background, marking stale PCs offline and
    notifying connected dashboards over the websocket."""
    while True:
        try:
            db = SessionLocal()
            try:
                stale = await asyncio.to_thread(mark_stale_computers_offline, db)
                for computer in stale:
                    logger.info("Marked offline (stale): %s", computer.hostname)
                    await manager.broadcast({
                        "type": "computer_updated",
                        "agent_id": computer.agent_id,
                        "hostname": computer.hostname,
                        "is_online": False,
                    })
            finally:
                db.close()
        except Exception:
            logger.exception("Offline sweep failed")

        await asyncio.sleep(settings.OFFLINE_SWEEP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_offline_sweep_loop())
    yield
    task.cancel()


app = FastAPI(
    title="Lab Monitoring System",
    description="Lab PC monitoring and preventive maintenance system",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(agent_router)
app.include_router(maintenance_router)
app.include_router(computers_router)
app.include_router(ws_router)


@app.get("/")
def root():
    return {"message": "Lab Monitoring System API is running"}


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"status": "healthy", "database": "connected"}

    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}