from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.enums import MaintenanceFrequency
from app.schemas.computer import ComputerSummaryResponse
from app.schemas.maintenance import MaintenanceSummaryResponse, MaintenanceTaskResponse
from app.schemas.maintenance_log import (
    ComputerMaintenanceView,
    MaintenanceLogResponse,
    MaintenanceLogToggle,
)
from app.services import maintenance_service

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("/tasks", response_model=list[MaintenanceTaskResponse])
def get_tasks(
    frequency: MaintenanceFrequency | None = None,
    db: Session = Depends(get_db),
):
    """The task catalog seeded from the Excel (name, frequency, default responsible person)."""
    return maintenance_service.list_tasks(
        db, frequency=frequency.value if frequency else None
    )


@router.get("/summary", response_model=MaintenanceSummaryResponse)
def get_maintenance_summary(
    frequency: MaintenanceFrequency,
    period: str = Query(
        ...,
        description="'2026-08-W2' (biweekly), '2026-08' (monthly), or '2026-H1' (half-yearly)",
    ),
    db: Session = Depends(get_db),
):
    """Collective completion across every enrolled PC, for the checklist chart."""
    return maintenance_service.get_maintenance_summary(db, frequency.value, period)


@router.get("/computers", response_model=list[ComputerSummaryResponse])
def get_maintenance_computers(db: Session = Depends(get_db)):
    """All PCs enrolled for maintenance tracking, in master-list order."""
    return maintenance_service.list_computers_for_maintenance(db)


@router.get(
    "/computers/{computer_id}/checklist",
    response_model=ComputerMaintenanceView,
)
def get_computer_checklist(
    computer_id: int,
    period: str = Query(
        ...,
        description="'2026-08-W2' (biweekly), '2026-08' (monthly), or '2026-H1' (half-yearly)",
    ),
    frequency: MaintenanceFrequency | None = None,
    db: Session = Depends(get_db),
):
    """Live specs (from the agent) + that PC's checklist for one period."""
    view = maintenance_service.get_computer_maintenance_view(
        db, computer_id, period, frequency.value if frequency else None
    )
    if not view:
        raise HTTPException(status_code=404, detail="Computer not found")
    return view


@router.post(
    "/log",
    response_model=MaintenanceLogResponse,
    status_code=status.HTTP_200_OK,
    summary="Tick or untick one maintenance task for one computer/period",
)
def toggle_log(payload: MaintenanceLogToggle, db: Session = Depends(get_db)):
    try:
        return maintenance_service.toggle_maintenance_log(
            db,
            computer_id=payload.computer_id,
            maintenance_task_id=payload.maintenance_task_id,
            period_label=payload.period_label,
            completed=payload.completed,
            completed_by=payload.completed_by,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))