from pydantic import BaseModel, Field

from app.models.enums import MaintenanceFrequency
from app.schemas.common import ORMModel, TimestampSchema


class MaintenanceTaskBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    default_frequency: MaintenanceFrequency = MaintenanceFrequency.BIWEEKLY
    responsible_person: str | None = Field(default=None, max_length=200)
    is_active: bool = True


class MaintenanceTaskCreate(MaintenanceTaskBase):
    pass


class MaintenanceTaskUpdate(BaseModel):
    description: str | None = None
    default_frequency: MaintenanceFrequency | None = None
    responsible_person: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None


class MaintenanceTaskResponse(MaintenanceTaskBase, TimestampSchema, ORMModel):
    id: int


class TaskCompletionSummary(BaseModel):
    """How many of the enrolled PCs have this task ticked for one period."""

    task_id: int
    task_name: str
    completed_count: int
    total_count: int
    percent: float


class LabSectionCompletionSummary(BaseModel):
    """Completion across every task × every PC in one lab section, for one period."""

    lab_section: str
    completed_count: int
    total_count: int
    percent: float


class MaintenanceSummaryResponse(BaseModel):
    """
    Aggregated view of the checklist across every enrolled PC for one
    frequency + period — the data behind the collective checklist
    chart (Categories/Maintenance overview), as opposed to the
    per-PC checklist view.
    """

    frequency: MaintenanceFrequency
    period_label: str
    total_computers: int
    total_tasks: int
    completed_count: int
    total_count: int
    percent: float
    by_task: list[TaskCompletionSummary]
    by_lab_section: list[LabSectionCompletionSummary]