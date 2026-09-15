from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import computer_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post(
    "/{alert_id}/acknowledge",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete an alert from the panel",
)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    try:
        computer_service.delete_alert(db, alert_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))