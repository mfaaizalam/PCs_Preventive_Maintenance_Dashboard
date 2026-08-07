from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine


app = FastAPI(
    title="Lab Monitoring System",
    description="Lab PC monitoring and preventive maintenance system",
    version="1.0.0",
)


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