from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class MetricHistoryBase(BaseModel):
    cpu_usage_percent: float | None = Field(default=None, ge=0, le=100)
    ram_usage_percent: float | None = Field(default=None, ge=0, le=100)
    disk_usage_percent: float | None = Field(default=None, ge=0, le=100)
    cpu_temperature_celsius: float | None = None
    recorded_at: datetime | None = None


class MetricHistoryCreate(MetricHistoryBase):
    computer_id: int


class MetricHistoryResponse(MetricHistoryBase, ORMModel):
    id: int
    computer_id: int
    recorded_at: datetime
