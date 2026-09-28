from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import require_it_manager
from app.db.database import get_db
from app.models.user import User
from app.schemas.computer import (
    AgentPauseBulkResponse,
    AgentPauseRequest,
    AgentPauseResponse,
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


# ----------------------------------------------------------------------
# AGENT MONITORING PAUSE / RESUME (audit mode) - IT Manager only.
# The agent actually stops reporting while paused; this is a real
# stop/start control, not a way to hide the agent from the OS.
# ----------------------------------------------------------------------

def _broadcast_pause_state(computer) -> None:
    asyncio.create_task(manager.broadcast({
        "type": "computer_updated",
        "agent_id": computer.agent_id,
        "hostname": computer.hostname,
        "monitoring_paused": computer.monitoring_paused,
        "pending_pause": computer.pending_pause,
        "pending_resume": computer.pending_resume,
    }))


@router.post(
    "/{computer_id}/pause-agent",
    response_model=AgentPauseResponse,
    summary="[IT Manager only] Flag one PC's agent to stop on its next check-in",
)
def pause_agent(
    computer_id: int,
    payload: AgentPauseRequest,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_it_manager),
):
    try:
        computer = computer_service.request_pause_agent(db, computer_id, payload.requested_by)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    _broadcast_pause_state(computer)
    return computer


@router.post(
    "/{computer_id}/resume-agent",
    response_model=AgentPauseResponse,
    summary="[IT Manager only] Flag one PC's agent to resume on its next check-in",
)
def resume_agent(
    computer_id: int,
    payload: AgentPauseRequest,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_it_manager),
):
    try:
        computer = computer_service.request_resume_agent(db, computer_id, payload.requested_by)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    _broadcast_pause_state(computer)
    return computer


@router.post(
    "/pause-all",
    response_model=AgentPauseBulkResponse,
    summary="[IT Manager only] Flag every online PC's agent to stop (optionally scoped to one lab)",
)
def pause_all_agents(
    payload: AgentPauseRequest,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_it_manager),
):
    computers = computer_service.request_pause_all(db, payload.requested_by, payload.lab_section)
    for computer in computers:
        _broadcast_pause_state(computer)

    return {
        "lab_section": payload.lab_section,
        "affected_count": len(computers),
        "computers": computers,
    }


@router.post(
    "/resume-all",
    response_model=AgentPauseBulkResponse,
    summary="[IT Manager only] Flag every paused PC's agent to resume (optionally scoped to one lab)",
)
def resume_all_agents(
    payload: AgentPauseRequest,
    db: Session = Depends(get_db),
    _manager: User = Depends(require_it_manager),
):
    computers = computer_service.request_resume_all(db, payload.requested_by, payload.lab_section)
    for computer in computers:
        _broadcast_pause_state(computer)

    return {
        "lab_section": payload.lab_section,
        "affected_count": len(computers),
        "computers": computers,
    }