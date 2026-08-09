from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import PeripheralStatus, PeripheralType
from app.schemas.common import ORMModel, TimestampSchema


class PeripheralBase(BaseModel):
    device_key: str = Field(..., max_length=255)
    device_type: PeripheralType
    vendor_id: str | None = Field(default=None, max_length=20)
    product_id: str | None = Field(default=None, max_length=20)
    serial_number: str | None = Field(default=None, max_length=100)
    port_path: str | None = Field(default=None, max_length=255)
    friendly_name: str | None = Field(default=None, max_length=200)
    model: str | None = Field(default=None, max_length=200)
    capacity_gb: float | None = Field(default=None, ge=0)
    volume_label: str | None = Field(default=None, max_length=100)
    descriptor: str | None = None
    status: PeripheralStatus = PeripheralStatus.DISCONNECTED
    is_expected: bool = True
    last_seen_at: datetime | None = None


class PeripheralCreate(PeripheralBase):
    computer_id: int


class PeripheralUpsert(PeripheralBase):
    pass


class PeripheralUpdate(BaseModel):
    friendly_name: str | None = Field(default=None, max_length=200)
    status: PeripheralStatus | None = None
    is_expected: bool | None = None
    last_seen_at: datetime | None = None


class PeripheralResponse(PeripheralBase, TimestampSchema, ORMModel):
    id: int
    computer_id: int
