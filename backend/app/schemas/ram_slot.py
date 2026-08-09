from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, TimestampSchema


class RamSlotBase(BaseModel):
    slot_number: int = Field(..., ge=0)
    capacity_gb: float | None = Field(default=None, ge=0)
    manufacturer: str | None = Field(default=None, max_length=100)
    speed_mhz: int | None = Field(default=None, ge=0)
    serial_number: str | None = Field(default=None, max_length=100)


class RamSlotCreate(RamSlotBase):
    computer_id: int


class RamSlotUpsert(RamSlotBase):
    pass


class RamSlotUpdate(BaseModel):
    capacity_gb: float | None = Field(default=None, ge=0)
    manufacturer: str | None = Field(default=None, max_length=100)
    speed_mhz: int | None = Field(default=None, ge=0)
    serial_number: str | None = Field(default=None, max_length=100)


class RamSlotResponse(RamSlotBase, TimestampSchema, ORMModel):
    id: int
    computer_id: int
