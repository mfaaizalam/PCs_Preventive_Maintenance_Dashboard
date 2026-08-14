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