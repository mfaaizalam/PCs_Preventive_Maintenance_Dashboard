from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.alert import AlertResponse
from app.services import computer_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
    summary="Dismiss an alert from the panel",
)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    try:
        return computer_service.acknowledge_alert(db, alert_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))