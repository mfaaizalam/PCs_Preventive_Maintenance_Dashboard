from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class MaintenanceLogToggle(BaseModel):
    """Body for ticking/unticking a single checklist box."""

    computer_id: int
    maintenance_task_id: int
    period_label: str = Field(
        ..., max_length=50,
        description="e.g. '2026-08-W2' (biweekly), '2026-08' (monthly), '2026-H1' (half-yearly)",
    )
    completed: bool
    completed_by: str | None = Field(default=None, max_length=200)
    notes: str | None = None


class MaintenanceLogResponse(ORMModel):
    id: int
    computer_id: int
    maintenance_task_id: int
    period_label: str
    completed: bool
    completed_by: str | None
    completed_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class MaintenanceChecklistItem(BaseModel):
    """One row of the checklist for one computer, one period."""

    task_id: int
    task_name: str
    frequency: str
    responsible_person: str | None
    period_label: str
    log_id: int | None
    completed: bool
    completed_by: str | None
    completed_at: datetime | None
    notes: str | None


class ComputerMaintenanceView(BaseModel):
    """Specs pulled live from Computer + that PC's checklist for one period."""

    computer_id: int
    s_no: int | None
    hostname: str
    lab_section: str | None
    cpu_model: str | None
    ram_total_gb: float | None
    disk_total_gb: float | None
    checklist: list[MaintenanceChecklistItem]