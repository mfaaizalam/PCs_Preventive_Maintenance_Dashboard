import logging
import time
import uuid
from datetime import datetime, timezone
import os
import config
from collectors.hardware import get_hardware_info
from collectors.licenses import get_license_info
from collectors.peripherals import get_peripherals
from collectors.software import get_software_inventory
from collectors.system import get_system_info
from services.api_client import send_report
from collectors.hardware import get_system_uuid
import psutil 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("agent")


# ============================================================
# AGENT IDENTITY
# ============================================================

def get_or_create_agent_id() -> str:
    os.makedirs(config.AGENT_ID_DIR, exist_ok=True)

    try:
        with open(config.AGENT_ID_FILE, "r", encoding="utf-8") as f:
            agent_id = f.read().strip()
            if agent_id:
                return agent_id
    except FileNotFoundError:
        pass

    agent_id = uuid.uuid4().hex

    with open(config.AGENT_ID_FILE, "w", encoding="utf-8") as f:
        f.write(agent_id)

    return agent_id


# ============================================================
# RAW COLLECTION
# ============================================================

def collect_raw() -> dict:
    return {
        "system": get_system_info(),
        "hardware": get_hardware_info(),
        "licenses": get_license_info(),
        "peripherals": get_peripherals(),
        "software": get_software_inventory(),
    }


# ============================================================
# MAPPING HELPERS: raw collector output -> AgentReportPayload shape
# ============================================================

def _map_storage_device_type(media_type: str | None) -> str:
    if not media_type:
        return "other"
    value = media_type.upper()
    if "NVME" in value:
        return "nvme"
    if "SSD" in value:
        return "ssd"
    if "HDD" in value or "HARD" in value:
        return "hdd"
    return "other"


def _map_storage_health(status: str | None) -> str:
    if not status:
        return "unknown"
    value = status.lower()
    if value in ("healthy", "ok"):
        return "healthy"
    if value in ("warning", "degraded"):
        return "warning"
    if value in ("unhealthy", "critical", "failed", "failing"):
        return "critical"
    return "unknown"


def _map_peripheral_type(device_type: str | None) -> str:
    mapping = {
        "keyboard": "keyboard",
        "mouse": "mouse",
        "touchpad": "mouse",
        "physical_printer": "printer",
        "virtual_printer": "printer",
        "bluetooth_speaker": "headset",       # closest match in enum
        "external_ssd": "usb_storage",
        "external_storage": "usb_storage",
    }
    return mapping.get((device_type or "").lower(), "other")


def _map_peripheral_status(raw_status) -> str:
    if raw_status is None:
        return "connected"
    value = str(raw_status).lower()
    if value in ("ok", "online"):
        return "connected"
    if value == "offline":
        return "disconnected"
    return "connected"


def _map_license_status(raw_status: str | None) -> str:
    if not raw_status:
        return "unknown"
    value = raw_status.lower()
    if "licensed" in value:
        return "active"
    if "notification" in value:
        return "expiring_soon"
    if "unlicensed" in value or "not installed" in value:
        return "not_activated"
    return "unknown"


def _parse_registry_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y%m%d", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _parse_wmi_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").date().isoformat()
    except ValueError:
        return None


def _build_ram_slots(ram_modules: list[dict]) -> list[dict]:
    slots = []
    for index, module in enumerate(ram_modules):
        slot_label = module.get("slot") or ""
        digits = "".join(ch for ch in slot_label if ch.isdigit())
        slot_number = int(digits) if digits else index
        slots.append({
            "slot_number": slot_number,
            "capacity_gb": module.get("capacity_gb"),
            "manufacturer": module.get("manufacturer"),
            "speed_mhz": module.get("speed_mhz"),
            "serial_number": None,
        })
    return slots


def _build_storage_devices(storage_list: list[dict], storage_health_list: list[dict]) -> list[dict]:
    health_by_serial = {
        h.get("serial_number"): h
        for h in storage_health_list
        if h.get("serial_number")
    }

    devices = []
    for disk in storage_list:
        serial = disk.get("serial_number")
        health = health_by_serial.get(serial, {})
        devices.append({
            "device_identifier": disk.get("device") or serial or disk.get("model") or "unknown",
            "device_type": _map_storage_device_type(disk.get("media_type") or health.get("media_type")),
            "model": disk.get("model"),
            "capacity_gb": disk.get("size_gb"),
            "health_status": _map_storage_health(health.get("health_status")),
            "smart_status": health.get("operational_status"),
            "serial_number": serial,
        })
    return devices


def _build_peripherals(peripheral_list: list[dict]) -> list[dict]:
    peripherals = []
    for device in peripheral_list:
        device_key = device.get("device_id") or device.get("name") or "unknown"
        peripherals.append({
            "device_key": device_key,
            "device_type": _map_peripheral_type(device.get("device_type")),
            "friendly_name": device.get("name"),
            "status": _map_peripheral_status(device.get("status")),
            "is_expected": not device.get("is_virtual", False),
        })
    return peripherals


def _build_software_licenses(license_info: dict) -> list[dict]:
    licenses = []

    windows = license_info.get("windows") or {}
    if windows.get("available"):
        licenses.append({
            "product_name": windows.get("product") or "Windows",
            "vendor": "Microsoft",
            "license_type": "perpetual",
            "status": _map_license_status(windows.get("license_status")),
            "expiry_date": _parse_wmi_date(windows.get("expiration_date")),
            "is_activated": windows.get("license_status") == "Licensed",
            "detected_automatically": True,
            "notes": windows.get("error"),
        })

    office = license_info.get("office") or {}
    if office.get("installed"):
        licenses.append({
            "product_name": office.get("product") or "Microsoft Office",
            "vendor": "Microsoft",
            "license_type": "unknown",
            "status": _map_license_status(office.get("license_status")),
            "expiry_date": None,
            "is_activated": office.get("license_status") == "Licensed",
            "detected_automatically": True,
            "notes": office.get("error"),
        })

    return licenses


def _build_installed_software(software_list: list[dict]) -> list[dict]:
    return [
        {
            "name": entry.get("name"),
            "publisher": entry.get("publisher"),
            "version": entry.get("version"),
            "install_date": _parse_registry_date(entry.get("install_date")),
            "is_authorized": None,
        }
        for entry in software_list
    ]


# ============================================================
# BUILD FULL PAYLOAD (matches AgentReportPayload schema)
# ============================================================

def build_report_payload(agent_id: str, raw: dict, hardware_uuid: str | None) -> dict:
    system = raw["system"]
    hardware = raw["hardware"]

    ram_modules = hardware.get("ram", [])
    ram_total_gb = round(sum(m.get("capacity_gb") or 0 for m in ram_modules), 2) or None

    disk_usage_list = hardware.get("disk_usage", [])
    main_drive = next(
        (d for d in disk_usage_list if str(d.get("drive", "")).upper().startswith("C")),
        None,
    )
    disk_total_gb = main_drive.get("total_gb") if main_drive else None

    cpu_list = hardware.get("cpu", [])
    cpu_model = cpu_list[0].get("name") if cpu_list else None

    now_iso = datetime.now(timezone.utc).isoformat()

    return {
        "agent_id": agent_id,
        "asset_id": config.ASSET_ID,
        "hardware_uuid": hardware_uuid,
        "hostname": system.get("hostname"),
        "ip_address": system.get("ip_address"),
        "lab_name": config.LAB_NAME,
        "lab_section": config.LAB_SECTION,
        "os_name": system.get("operating_system"),
        "os_version": system.get("os_version"),
        "cpu_model": cpu_model,
        "cpu_usage_percent": system.get("cpu_usage"),
        "cpu_temperature_celsius": None,
        "ram_total_gb": ram_total_gb,
        "ram_usage_percent": system.get("ram_usage"),
        "disk_total_gb": disk_total_gb,
        "disk_usage_percent": system.get("disk_usage"),
        "uptime_seconds": system.get("uptime_seconds"),
        "is_online": True,
        "reported_at": now_iso,
        "ram_slots": _build_ram_slots(ram_modules),
        "storage_devices": _build_storage_devices(
            hardware.get("storage", []),
            hardware.get("storage_health", []),
        ),
        "peripherals": _build_peripherals(raw["peripherals"]),
        "peripheral_events": [],
        "software_licenses": _build_software_licenses(raw["licenses"]),
        "installed_software": _build_installed_software(raw["software"]),
        "metrics": {
            "cpu_usage_percent": system.get("cpu_usage"),
            "ram_usage_percent": system.get("ram_usage"),
            "disk_usage_percent": system.get("disk_usage"),
            "cpu_temperature_celsius": None,
            "recorded_at": now_iso,
        },
    }


# ============================================================
# MAIN LOOP - runs forever, one report every REPORT_INTERVAL_SECONDS
# ============================================================
def run_forever():
    agent_id = get_or_create_agent_id()
    psutil.cpu_percent(interval=None)

    # Static for the life of the process - computed once, not every cycle.
    hardware_uuid = get_system_uuid()

    logger.info(
        "Agent starting | agent_id=%s | hardware_uuid=%s | fast_interval=%ss | slow_interval=%ss | target=%s",
        agent_id,
        hardware_uuid,
        config.FAST_REPORT_INTERVAL_SECONDS,
        config.SLOW_REPORT_INTERVAL_SECONDS,
        config.AGENT_REPORT_URL,
    )

    def collect_slow():
        return {
            "hardware": get_hardware_info(),
            "licenses": get_license_info(),
            "software": get_software_inventory(),
        }

    slow_raw = collect_slow()
    last_slow_refresh = time.monotonic()

    while True:
        cycle_start = time.monotonic()

        try:
            if time.monotonic() - last_slow_refresh >= config.SLOW_REPORT_INTERVAL_SECONDS:
                slow_raw = collect_slow()
                last_slow_refresh = time.monotonic()
                logger.info("Refreshed hardware/software/license inventory")

            raw = {
                "system": get_system_info(),
                "peripherals": get_peripherals(),
                **slow_raw,
            }
            payload = build_report_payload(agent_id, raw, hardware_uuid)
            result = send_report(payload)

            if result:
                logger.info(
                    "Synced OK | computer_id=%s | status=%s",
                    result.get("id"),
                    result.get("status"),
                )

        except Exception:
            logger.exception("Unexpected error during collection/report cycle")

        elapsed = time.monotonic() - cycle_start
        sleep_for = max(0, config.FAST_REPORT_INTERVAL_SECONDS - elapsed)
        time.sleep(sleep_for)


if __name__ == "__main__":
    try:
        run_forever()
    except KeyboardInterrupt:
        logger.info("Agent stopped by user.")