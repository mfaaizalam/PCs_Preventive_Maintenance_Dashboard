from app.schemas.agent import AgentReportPayload, DashboardOverviewResponse
from app.schemas.alert import (
    AlertAcknowledge,
    AlertCreate,
    AlertResponse,
    AlertSummaryResponse,
)
from app.schemas.audit_log import AuditLogCreate, AuditLogResponse
from app.schemas.computer import (
    ComputerCreate,
    ComputerIngest,
    ComputerResponse,
    ComputerSummaryResponse,
    ComputerUpdate,
)
from app.schemas.hardware_change_log import (
    HardwareChangeLogCreate,
    HardwareChangeLogResponse,
)
from app.schemas.installed_software import (
    InstalledSoftwareCreate,
    InstalledSoftwareResponse,
    InstalledSoftwareUpdate,
    InstalledSoftwareUpsert,
)
from app.schemas.maintenance import (
    MaintenanceTaskCreate,
    MaintenanceTaskResponse,
    MaintenanceTaskUpdate,
)
from app.schemas.maintenance_log import (
    ComputerMaintenanceView,
    MaintenanceChecklistItem,
    MaintenanceLogResponse,
    MaintenanceLogToggle,
)
from app.schemas.notification import HardwareEventBrief, HardwareNotificationResponse
from app.schemas.peripheral import (
    PeripheralCreate,
    PeripheralResponse,
    PeripheralUpdate,
    PeripheralUpsert,
)
from app.schemas.peripheral_event import PeripheralEventCreate, PeripheralEventResponse
from app.schemas.ram_slot import RamSlotCreate, RamSlotResponse, RamSlotUpdate, RamSlotUpsert
from app.schemas.software_license import (
    SoftwareLicenseCreate,
    SoftwareLicenseResponse,
    SoftwareLicenseUpdate,
    SoftwareLicenseUpsert,
)
from app.schemas.storage_device import (
    StorageDeviceCreate,
    StorageDeviceResponse,
    StorageDeviceUpdate,
    StorageDeviceUpsert,
)
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse, UserUpdate

__all__ = [
    "AgentReportPayload",
    "AlertAcknowledge",
    "AlertCreate",
    "AlertResponse",
    "AlertSummaryResponse",
    "AuditLogCreate",
    "AuditLogResponse",
    "ComputerCreate",
    "ComputerIngest",
    "ComputerMaintenanceView",
    "ComputerResponse",
    "ComputerSummaryResponse",
    "ComputerUpdate",
    "DashboardOverviewResponse",
    "HardwareChangeLogCreate",
    "HardwareChangeLogResponse",
    "HardwareEventBrief",
    "HardwareNotificationResponse",
    "InstalledSoftwareCreate",
    "InstalledSoftwareResponse",
    "InstalledSoftwareUpdate",
    "InstalledSoftwareUpsert",
    "MaintenanceChecklistItem",
    "MaintenanceLogResponse",
    "MaintenanceLogToggle",
    "MaintenanceTaskCreate",
    "MaintenanceTaskResponse",
    "MaintenanceTaskUpdate",
    "PeripheralCreate",
    "PeripheralEventCreate",
    "PeripheralEventResponse",
    "PeripheralResponse",
    "PeripheralUpdate",
    "PeripheralUpsert",
    "RamSlotCreate",
    "RamSlotResponse",
    "RamSlotUpdate",
    "RamSlotUpsert",
    "SoftwareLicenseCreate",
    "SoftwareLicenseResponse",
    "SoftwareLicenseUpdate",
    "SoftwareLicenseUpsert",
    "StorageDeviceCreate",
    "StorageDeviceResponse",
    "StorageDeviceUpdate",
    "StorageDeviceUpsert",
    "TokenResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
]