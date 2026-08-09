from pydantic import BaseModel, Field

from app.models.enums import MaintenanceFrequency
from app.schemas.common import ORMModel, TimestampSchema


class MaintenanceAssetBase(BaseModel):
    pc_no: str = Field(..., max_length=50)
    lab_section: str = Field(..., max_length=100)
    specification: str | None = None
    asset_id: str | None = Field(default=None, max_length=50)
    default_owner: str | None = Field(default=None, max_length=200)
    is_active: bool = True


class MaintenanceAssetCreate(MaintenanceAssetBase):
    pass


class MaintenanceAssetUpdate(BaseModel):
    lab_section: str | None = Field(default=None, max_length=100)
    specification: str | None = None
    asset_id: str | None = Field(default=None, max_length=50)
    default_owner: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None


class MaintenanceAssetResponse(MaintenanceAssetBase, TimestampSchema, ORMModel):
    id: int


class MaintenanceTaskBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    default_frequency: MaintenanceFrequency = MaintenanceFrequency.BIWEEKLY
    is_active: bool = True


class MaintenanceTaskCreate(MaintenanceTaskBase):
    pass


class MaintenanceTaskUpdate(BaseModel):
    description: str | None = None
    default_frequency: MaintenanceFrequency | None = None
    is_active: bool | None = None


class MaintenanceTaskResponse(MaintenanceTaskBase, TimestampSchema, ORMModel):
    id: int
