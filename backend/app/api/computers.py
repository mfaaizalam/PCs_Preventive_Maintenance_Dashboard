from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.computer import ComputerManualCreate, ComputerResponse
from app.services import computer_service

router = APIRouter(prefix="/api/computers", tags=["computers"])


@router.post(
    "",
    response_model=ComputerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manually add a PC that has no monitoring agent installed",
)
def create_computer(payload: ComputerManualCreate, db: Session = Depends(get_db)):
    try:
        return computer_service.create_manual_computer(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.delete(
    "/{computer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a PC",
)
def remove_computer(computer_id: int, db: Session = Depends(get_db)):
    if not computer_service.delete_computer(db, computer_id):
        raise HTTPException(status_code=404, detail="Computer not found")

