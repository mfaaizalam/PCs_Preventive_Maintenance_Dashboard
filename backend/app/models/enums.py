import enum


class ComputerStatus(str, enum.Enum):
    HEALTHY = "healthy"
    ATTENTION = "attention"
    CRITICAL = "critical"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class StorageDeviceType(str, enum.Enum):
    HDD = "hdd"
    SSD = "ssd"
    NVME = "nvme"
    OTHER = "other"


class StorageHealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class PeripheralType(str, enum.Enum):
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    MONITOR = "monitor"
    PRINTER = "printer"
    USB_STORAGE = "usb_storage"
    WEBCAM = "webcam"
    HEADSET = "headset"
    DOCKING_STATION = "docking_station"
    OTHER = "other"


class PeripheralStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    MISSING = "missing"
    UNAUTHORIZED = "unauthorized"


class PeripheralEventType(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class LicenseType(str, enum.Enum):
    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    SEAT_BASED = "seat_based"
    TRIAL = "trial"
    UNKNOWN = "unknown"


class LicenseStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    RENEWED = "renewed"
    NOT_ACTIVATED = "not_activated"
    UNKNOWN = "unknown"


class AlertType(str, enum.Enum):
    PERFORMANCE = "performance"
    SECURITY = "security"
    LICENSE = "license"
    HARDWARE = "hardware"
    CONNECTIVITY = "connectivity"
    MAINTENANCE = "maintenance"
    INVENTORY = "inventory"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MaintenanceFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    HALF_YEARLY = "half_yearly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    LAB_STAFF = "lab_staff"
    VIEWER = "viewer"
    AUDITOR = "auditor"


class HardwareChangeType(str, enum.Enum):
    RAM = "ram"
    STORAGE = "storage"
    PERIPHERAL = "peripheral"
    CPU = "cpu"
    NETWORK = "network"
    SOFTWARE = "software"
    OTHER = "other"