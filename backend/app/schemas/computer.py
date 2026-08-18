from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ComputerStatus
from app.schemas.common import ORMModel, TimestampSchema
from app.schemas.notification import HardwareEventBrief


class ComputerBase(BaseModel):
    agent_id: str = Field(..., max_length=100)
    asset_id: str | None = Field(default=None, max_length=50)
    hardware_uuid: str | None = Field(default=None, max_length=100)
    hostname: str = Field(..., max_length=100)
    ip_address: str | None = Field(default=None, max_length=45)
    lab_name: str | None = Field(default=None, max_length=100)
    lab_section: str | None = Field(default=None, max_length=100)
    os_name: str | None = Field(default=None, max_length=100)
    os_version: str | None = Field(default=None, max_length=100)
    cpu_model: str | None = Field(default=None, max_length=200)
    cpu_usage_percent: float | None = Field(default=None, ge=0, le=100)
    cpu_temperature_celsius: float | None = None
    ram_total_gb: float | None = Field(default=None, ge=0)
    ram_usage_percent: float | None = Field(default=None, ge=0, le=100)
    disk_total_gb: float | None = Field(default=None, ge=0)
    disk_usage_percent: float | None = Field(default=None, ge=0, le=100)
    uptime_seconds: int | None = Field(default=None, ge=0)
    status: ComputerStatus = ComputerStatus.UNKNOWN
    is_online: bool = False
    last_seen: datetime | None = None


class ComputerCreate(ComputerBase):
    pass


class ComputerUpdate(BaseModel):
    asset_id: str | None = Field(default=None, max_length=50)
    hardware_uuid: str | None = Field(default=None, max_length=100)
    hostname: str | None = Field(default=None, max_length=100)
    ip_address: str | None = Field(default=None, max_length=45)
    lab_name: str | None = Field(default=None, max_length=100)
    lab_section: str | None = Field(default=None, max_length=100)
    os_name: str | None = Field(default=None, max_length=100)
    os_version: str | None = Field(default=None, max_length=100)
    cpu_model: str | None = Field(default=None, max_length=200)
    cpu_usage_percent: float | None = Field(default=None, ge=0, le=100)
    cpu_temperature_celsius: float | None = None
    ram_total_gb: float | None = Field(default=None, ge=0)
    ram_usage_percent: float | None = Field(default=None, ge=0, le=100)
    disk_total_gb: float | None = Field(default=None, ge=0)
    disk_usage_percent: float | None = Field(default=None, ge=0, le=100)
    uptime_seconds: int | None = Field(default=None, ge=0)
    status: ComputerStatus | None = None
    is_online: bool | None = None
    last_seen: datetime | None = None


class ComputerIngest(ComputerUpdate):
    agent_id: str = Field(..., max_length=100)


class ComputerResponse(ComputerBase, TimestampSchema, ORMModel):
    id: int


class ComputerSummaryResponse(ORMModel):
    id: int
    agent_id: str
    asset_id: str | None
    hostname: str
    lab_name: str | None
    lab_section: str | None
    status: ComputerStatus
    is_online: bool
    ip_address: str | None = None
    cpu_usage_percent: float | None
    ram_usage_percent: float | None
    disk_usage_percent: float | None
    uptime_seconds: int | None = None
    last_seen: datetime | None
    # Last 3 days of hardware connect/disconnect activity for this PC
    # (most recent first, capped). Populated by
    # computer_service.get_dashboard_overview - not a DB column.
    recent_hardware_events: list[HardwareEventBrief] = Field(default_factory=list)