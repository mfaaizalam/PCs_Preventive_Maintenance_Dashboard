from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import PeripheralEventType
from app.schemas.common import ORMModel


class PeripheralEventBase(BaseModel):
    event_type: PeripheralEventType
    device_type: str | None = Field(default=None, max_length=30)
    device_key: str | None = Field(default=None, max_length=255)
    vendor_id: str | None = Field(default=None, max_length=20)
    product_id: str | None = Field(default=None, max_length=20)
    serial_number: str | None = Field(default=None, max_length=100)
    port_path: str | None = Field(default=None, max_length=255)
    details: str | None = None
    occurred_at: datetime | None = None


class PeripheralEventCreate(PeripheralEventBase):
    computer_id: int
    peripheral_id: int | None = None


class PeripheralEventResponse(PeripheralEventBase, ORMModel):
    id: int
    computer_id: int
    peripheral_id: int | None
    occurred_at: datetime
