from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.computer import ComputerMetadataUpdate, ComputerSummaryResponse
from app.services import computer_service

router = APIRouter(prefix="/api/computers", tags=["computers"])


# NOTE: manual "Add PC" creation was removed in Module 2 - every PC in
# this system now comes from a real agent check-in (POST
# /api/agent/report), which also auto-identifies its lab/PC number
# from the hostname (see computer_service._derive_lab_from_hostname).
# Deletion is kept: it's still how a genuine duplicate computer row
# (see the hostname-collision error in ingest_agent_report) gets
# cleaned up. Retiring a stale/replaced PC is now automatic (see
# computer_service.auto_retire_stale_computers) and doesn't need this.


@router.patch(
    "/{computer_id}",
    response_model=ComputerSummaryResponse,
    summary="Edit a PC's department / lab name / asset ID (dashboard pencil icon)",
)
def update_computer(
    computer_id: int,
    payload: ComputerMetadataUpdate,
    db: Session = Depends(get_db),
):
    try:
        computer = computer_service.update_computer_metadata(
            db,
            computer_id,
            department=payload.department,
            lab_section=payload.lab_section,
            asset_id=payload.asset_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    if computer is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return computer


@router.delete(
    "/{computer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a PC",
)
def remove_computer(computer_id: int, db: Session = Depends(get_db)):
    if not computer_service.delete_computer(db, computer_id):
        raise HTTPException(status_code=404, detail="Computer not found")