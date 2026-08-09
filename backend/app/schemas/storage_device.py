from pydantic import BaseModel, Field

from app.models.enums import StorageDeviceType, StorageHealthStatus
from app.schemas.common import ORMModel, TimestampSchema


class StorageDeviceBase(BaseModel):
    device_identifier: str = Field(..., max_length=200)
    device_type: StorageDeviceType = StorageDeviceType.OTHER
    model: str | None = Field(default=None, max_length=200)
    capacity_gb: float | None = Field(default=None, ge=0)
    health_status: StorageHealthStatus = StorageHealthStatus.UNKNOWN
    smart_status: str | None = None
    serial_number: str | None = Field(default=None, max_length=100)


class StorageDeviceCreate(StorageDeviceBase):
    computer_id: int


class StorageDeviceUpsert(StorageDeviceBase):
    pass


class StorageDeviceUpdate(BaseModel):
    device_type: StorageDeviceType | None = None
    model: str | None = Field(default=None, max_length=200)
    capacity_gb: float | None = Field(default=None, ge=0)
    health_status: StorageHealthStatus | None = None
    smart_status: str | None = None
    serial_number: str | None = Field(default=None, max_length=100)


class StorageDeviceResponse(StorageDeviceBase, TimestampSchema, ORMModel):
    id: int
    computer_id: int
