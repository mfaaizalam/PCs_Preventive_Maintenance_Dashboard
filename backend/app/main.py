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
from app.api.alerts import router as alerts_router
from app.api.ws import router as ws_router
from app.services.computer_service import auto_retire_stale_computers, mark_stale_computers_offline
from app.services import retention_service
from app.ws_manager import manager


logger = logging.getLogger("app.cleanup")

DB_KEEPALIVE_INTERVAL_SECONDS = 240


def _ping_db():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


async def _db_keepalive_loop():
    while True:
        try:
            await asyncio.to_thread(_ping_db)
            logger.info("DB keep-alive ping OK")
        except Exception:
            logger.exception("DB keep-alive ping failed")

        await asyncio.sleep(DB_KEEPALIVE_INTERVAL_SECONDS)

async def _offline_sweep_loop():
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

                retired = await asyncio.to_thread(auto_retire_stale_computers, db)
                for computer in retired:
                    logger.info(
                        "Auto-retired (offline %s+ days, not a mass outage): %s",
                        computer.retired_at,
                        computer.hostname,
                    )
                    await manager.broadcast({
                        "type": "computer_updated",
                        "agent_id": computer.agent_id,
                        "hostname": computer.hostname,
                        "is_retired": True,
                    })
            finally:
                db.close()
        except Exception:
            logger.exception("Offline sweep failed")

        await asyncio.sleep(settings.OFFLINE_SWEEP_INTERVAL_SECONDS)


async def _retention_sweep_loop():
    while True:
        try:
            db = SessionLocal()
            try:
                await asyncio.to_thread(retention_service.run_retention_sweep, db)
            finally:
                db.close()
        except Exception:
            logger.exception("Retention sweep failed")

        await asyncio.sleep(settings.RETENTION_SWEEP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    sweep_task = asyncio.create_task(_offline_sweep_loop())
    keepalive_task = asyncio.create_task(_db_keepalive_loop())
    retention_task = asyncio.create_task(_retention_sweep_loop())
    yield
    sweep_task.cancel()
    keepalive_task.cancel()
    retention_task.cancel()


app = FastAPI(
    title="Lab Monitoring System",
    description="Lab PC monitoring and preventive maintenance system",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(agent_router)
app.include_router(maintenance_router)
app.include_router(computers_router)
app.include_router(alerts_router)
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