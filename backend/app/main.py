import logging

from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine
from app.api.agent import router as agent_router
from app.api.maintenance import router as maintenance_router
from app.api.computers import router as computers_router

logger = logging.getLogger("app.cleanup")


app = FastAPI(
    title="Lab Monitoring System",
    description="Lab PC monitoring and preventive maintenance system",
    version="1.0.0",
)


# Agent routes
app.include_router(agent_router)
# Maintenance route
app.include_router(maintenance_router)
# Manual computer add/remove route
app.include_router(computers_router)

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