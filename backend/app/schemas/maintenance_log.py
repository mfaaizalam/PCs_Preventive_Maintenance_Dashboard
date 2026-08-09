from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class MaintenanceLogBase(BaseModel):
    maintenance_asset_id: int
    maintenance_task_id: int
    period_label: str = Field(..., max_length=50)
    responsible_person: str | None = Field(default=None, max_length=200)
    completed_by_id: int | None = None
    notes: str | None = None
    completed_at: datetime | None = None


class MaintenanceLogCreate(MaintenanceLogBase):
    pass


class MaintenanceLogResponse(MaintenanceLogBase, ORMModel):
    id: int
    completed_at: datetime
    created_at: datetime
