from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.alert import AlertSummaryResponse
from app.schemas.computer import ComputerSummaryResponse
from app.schemas.installed_software import InstalledSoftwareUpsert
from app.schemas.peripheral import PeripheralUpsert
from app.schemas.peripheral_event import PeripheralEventBase
from app.schemas.ram_slot import RamSlotUpsert
from app.schemas.software_license import SoftwareLicenseUpsert
from app.schemas.storage_device import StorageDeviceUpsert


class AgentMetricSnapshot(BaseModel):
    cpu_usage_percent: float | None = Field(default=None, ge=0, le=100)
    ram_usage_percent: float | None = Field(default=None, ge=0, le=100)
    disk_usage_percent: float | None = Field(default=None, ge=0, le=100)
    cpu_temperature_celsius: float | None = None
    recorded_at: datetime | None = None


class AgentReportPayload(BaseModel):
    """Compact payload sent by the monitoring agent on each check-in."""

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
    is_online: bool = True
    reported_at: datetime | None = None
    ram_slots: list[RamSlotUpsert] = Field(default_factory=list)
    storage_devices: list[StorageDeviceUpsert] = Field(default_factory=list)
    peripherals: list[PeripheralUpsert] = Field(default_factory=list)
    peripheral_events: list[PeripheralEventBase] = Field(default_factory=list)
    software_licenses: list[SoftwareLicenseUpsert] = Field(default_factory=list)
    installed_software: list[InstalledSoftwareUpsert] = Field(default_factory=list)
    metrics: AgentMetricSnapshot | None = None


class DashboardOverviewResponse(BaseModel):
    total_pcs: int
    healthy_count: int
    attention_count: int
    critical_count: int
    offline_count: int
    active_alert_count: int
    last_refresh_at: datetime | None = None
    computers: list[ComputerSummaryResponse] = Field(default_factory=list)
    recent_alerts: list[AlertSummaryResponse] = Field(default_factory=list)
