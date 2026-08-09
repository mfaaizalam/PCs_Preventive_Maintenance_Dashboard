from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import HardwareChangeType
from app.schemas.common import ORMModel


class HardwareChangeLogBase(BaseModel):
    change_type: HardwareChangeType
    entity_type: str | None = Field(default=None, max_length=50)
    entity_identifier: str | None = Field(default=None, max_length=255)
    field_name: str | None = Field(default=None, max_length=100)
    old_value: str | None = None
    new_value: str | None = None
    changed_at: datetime | None = None


class HardwareChangeLogCreate(HardwareChangeLogBase):
    computer_id: int


class HardwareChangeLogResponse(HardwareChangeLogBase, ORMModel):
    id: int
    computer_id: int
    changed_at: datetime
