from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.computer import (
    ComputerMetadataUpdate,
    ComputerSummaryResponse,
    LabShutdownResponse,
    ShutdownRequest,
    ShutdownResponse,
)
from app.services import computer_service
from app.ws_manager import manager
import asyncio

router = APIRouter(prefix="/api/computers", tags=["computers"])


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


@router.post(
    "/{computer_id}/shutdown",
    response_model=ShutdownResponse,
    summary="Flag one PC to shut down on its next check-in",
)
def shutdown_computer(
    computer_id: int,
    payload: ShutdownRequest,
    db: Session = Depends(get_db),
):
    try:
        computer = computer_service.request_shutdown(db, computer_id, payload.requested_by)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    asyncio.create_task(manager.broadcast({
        "type": "computer_updated",
        "agent_id": computer.agent_id,
        "hostname": computer.hostname,
        "pending_shutdown": True,
    }))
    return computer


@router.post(
    "/{computer_id}/shutdown/cancel",
    response_model=ShutdownResponse,
    summary="Cancel a still-pending shutdown before the agent has picked it up",
)
def cancel_computer_shutdown(computer_id: int, db: Session = Depends(get_db)):
    computer = computer_service.cancel_shutdown(db, computer_id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")

    asyncio.create_task(manager.broadcast({
        "type": "computer_updated",
        "agent_id": computer.agent_id,
        "hostname": computer.hostname,
        "pending_shutdown": False,
    }))
    return computer


@router.post(
    "/shutdown-lab",
    response_model=LabShutdownResponse,
    summary="Flag every online PC in one lab section to shut down on their next check-in",
)
def shutdown_lab_section(
    lab_section: str,
    payload: ShutdownRequest,
    db: Session = Depends(get_db),
):
    computers = computer_service.request_lab_shutdown(db, lab_section, payload.requested_by)

    for computer in computers:
        asyncio.create_task(manager.broadcast({
            "type": "computer_updated",
            "agent_id": computer.agent_id,
            "hostname": computer.hostname,
            "pending_shutdown": True,
        }))

    return {
        "lab_section": lab_section,
        "requested_count": len(computers),
        "computers": computers,
    }