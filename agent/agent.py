import json
import logging
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
import os
import config
from collectors.hardware import get_hardware_info
from collectors.licenses import get_license_info
from collectors.peripherals import get_peripherals
from collectors.software import get_software_inventory, get_tracked_software
from collectors.system import get_system_info
from services.api_client import send_report, send_shutdown_ack
from collectors.hardware import get_system_uuid
import psutil 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("agent")


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


def collect_raw() -> dict:
    return {
        "system": get_system_info(),
        "hardware": get_hardware_info(),
        "licenses": get_license_info(),
        "peripherals": get_peripherals(),
        "software": get_software_inventory(),
    }


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
        "bluetooth_speaker": "headset",
        "monitor": "monitor",
        "projector": "projector",
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


def _build_software_licenses(
    license_info: dict,
    software_list: list[dict],
) -> list[dict]:
    """
    Build license records for:
      1. Windows
      2. Microsoft Office
      3. Every software item in the project's required baseline.

    The project baseline is deliberately represented even when an application
    is not installed. This lets the dashboard answer both:
      - Is the required software installed?
      - Does the system have a verified license status?

    Detection alone never means "licensed".
    """

    licenses = []

    windows = license_info.get("windows") or {}
    if windows.get("available"):
        licenses.append({
            "product_name": windows.get("product") or "Windows",
            "vendor": "Microsoft",
            "license_type": "perpetual",
            "status": _map_license_status(
                windows.get("license_status")
            ),
            "expiry_date": _parse_wmi_date(
                windows.get("expiration_date")
            ),
            "is_activated": (
                windows.get("license_status") == "Licensed"
            ),
            "detected_automatically": True,
            "notes": windows.get("error"),
        })

    office = license_info.get("office") or {}
    if office.get("installed"):
        licenses.append({
            "product_name": office.get("product") or "Microsoft Office",
            "vendor": "Microsoft",
            "license_type": "unknown",
            "status": _map_license_status(
                office.get("license_status")
            ),
            "expiry_date": None,
            "is_activated": (
                office.get("license_status") == "Licensed"
            ),
            "detected_automatically": True,
            "notes": office.get("error"),
        })

    # ---------------------------------------------------------
    # REQUIRED PROJECT SOFTWARE
    # ---------------------------------------------------------
    tracked = get_tracked_software(software_list)

    for item in tracked:
        required_name = item["required_name"]
        installed = item.get("installed")

        if installed:
            installed_name = installed.get("name") or required_name
            version = installed.get("version")
            publisher = installed.get("publisher")

            licenses.append({
                "product_name": required_name,
                "vendor": publisher,
                "version": version,
                "license_type": "unknown",
                "status": "unknown",
                "expiry_date": None,
                "is_activated": False,
                "detected_automatically": True,
                "notes": (
                    f"Required software detected as "
                    f"'{installed_name}'. "
                    "Installation detected; license activation "
                    "was not independently verified by the agent."
                ),
            })
        else:
            licenses.append({
                "product_name": required_name,
                "vendor": None,
                "version": None,
                "license_type": "unknown",
                "status": "not_activated",
                "expiry_date": None,
                "is_activated": False,
                "detected_automatically": True,
                "notes": (
                    "Required by the project software baseline "
                    "but not detected in the Windows installed-software "
                    "registry."
                ),
            })

    return licenses

def _peripheral_snapshot_file() -> str:
    return os.path.join(
        config.AGENT_ID_DIR,
        "peripheral_snapshot.json",
    )


def _peripheral_identity(device: dict) -> str:
    """
    Build a stable identity for connect/disconnect tracking.
    Prefer the Windows DeviceID. Fall back to name/type when needed.
    """
    device_key = (
        device.get("device_id")
        or device.get("name")
        or "unknown"
    )
    device_type = device.get("device_type") or "other"

    return f"{device_type}|{device_key}"


def _load_peripheral_snapshot() -> dict:
    path = _peripheral_snapshot_file()

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        return data if isinstance(data, dict) else {}

    except (FileNotFoundError, OSError, ValueError):
        return {}


def _save_peripheral_snapshot(peripherals: list[dict]) -> None:
    snapshot = {
        _peripheral_identity(device): {
            "device_type": device.get("device_type"),
            "device_id": device.get("device_id"),
            "name": device.get("name"),
        }
        for device in peripherals
    }

    # Nothing changed -> no disk write (this runs every 30 seconds).
    if snapshot == _load_peripheral_snapshot():
        return

    os.makedirs(config.AGENT_ID_DIR, exist_ok=True)
    path = _peripheral_snapshot_file()
    temp_path = f"{path}.tmp"

    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            json.dump(snapshot, handle, indent=2)
        os.replace(temp_path, path)
    except OSError:
        logger.exception("Could not save peripheral snapshot")


def _build_peripheral_events(peripherals: list[dict]) -> list[dict]:
    """
    Generate CONNECTED events for devices that were not in the last
    snapshot that the server successfully received.

    The snapshot is NOT saved here. It is saved by the caller only after
    the report was accepted, so a failed send never loses an event.

    DISCONNECTED events are left to the backend's missing-device detection
    (the peripheral list is sent every 30 seconds), which avoids duplicates.
    """
    previous = _load_peripheral_snapshot()

    # First successful inventory creates a baseline only.
    if not previous:
        return []

    events = []
    for device in peripherals:
        key = _peripheral_identity(device)
        if key in previous:
            continue

        events.append({
            "event_type": "connected",
            "device_type": _map_peripheral_type(device.get("device_type")),
            "device_key": device.get("device_id") or device.get("name") or key,
            "details": (
                f"{device.get('name') or 'Device'} "
                "was newly detected by the agent."
            ),
        })

    return events


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


def build_report_payload(
    agent_id: str,
    raw: dict,
    hardware_uuid: str | None,
    full: bool = True,
) -> dict:
    """
    full=True  -> everything (sent at start and every 3 hours).
    full=False -> light report: usage metrics + peripherals only. The heavy
                  lists (installed_software, software_licenses, ram_slots,
                  storage_devices) are left OUT of the payload entirely.
    """
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

    payload = {
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
        "peripherals": _build_peripherals(raw["peripherals"]),
        "peripheral_events": _build_peripheral_events(
            raw["peripherals"]
        ),
        "metrics": {
            "cpu_usage_percent": system.get("cpu_usage"),
            "ram_usage_percent": system.get("ram_usage"),
            "disk_usage_percent": system.get("disk_usage"),
            "cpu_temperature_celsius": None,
            "recorded_at": now_iso,
        },
    }

    if full:
        payload["ram_slots"] = _build_ram_slots(ram_modules)
        payload["storage_devices"] = _build_storage_devices(
            hardware.get("storage", []),
            hardware.get("storage_health", []),
        )
        payload["software_licenses"] = _build_software_licenses(
            raw["licenses"],
            raw["software"],
        )
        payload["installed_software"] = _build_installed_software(raw["software"])

    return payload


def trigger_shutdown(agent_id: str) -> None:
    logger.warning(
        "Remote shutdown received - powering off in %ss",
        config.SHUTDOWN_GRACE_SECONDS,
    )
    try:
        subprocess.run(
            [
                "shutdown",
                "/s",
                "/t", str(config.SHUTDOWN_GRACE_SECONDS),
                "/c", "Remote shutdown requested from the Lab Monitoring dashboard.",
            ],
            check=True,
        )
    except Exception:
        logger.exception("Failed to invoke Windows shutdown")
        return

    send_shutdown_ack(agent_id)
    sys.exit(0)


def collect_slow() -> dict:
    """Heavy collectors (registry scan, WMI, PowerShell, OSPP licence check)."""
    return {
        "hardware": get_hardware_info(),
        "licenses": get_license_info(),
        "software": get_software_inventory(),
    }


def run_forever():
    agent_id = get_or_create_agent_id()
    psutil.cpu_percent(interval=None)

    hardware_uuid = get_system_uuid()

    logger.info(
        "Agent starting | agent_id=%s | hardware_uuid=%s | light_interval=%ss | full_interval=%ss | target=%s",
        agent_id,
        hardware_uuid,
        config.FAST_REPORT_INTERVAL_SECONDS,
        config.SLOW_REPORT_INTERVAL_SECONDS,
        config.AGENT_REPORT_URL,
    )

    slow_raw = None
    slow_collected_at = None
    last_full_ok = None  # monotonic time of the last FULL report the server accepted

    while True:
        cycle_start = time.monotonic()

        try:
            # A full report is due when none has succeeded yet (agent just
            # started, or the server was down at startup) or 3 hours have
            # passed since the last successful one. A failed full report
            # stays due, so it is retried every cycle until the server accepts it.
            full = (
                last_full_ok is None
                or cycle_start - last_full_ok >= config.SLOW_REPORT_INTERVAL_SECONDS
            )

            if full and (
                slow_raw is None
                or cycle_start - slow_collected_at >= config.INVENTORY_CACHE_SECONDS
            ):
                slow_raw = collect_slow()
                slow_collected_at = time.monotonic()
                logger.info("Collected hardware/software/license inventory")

            if slow_raw is None:  # cannot happen (first cycle is always full)
                continue

            raw = {
                "system": get_system_info(),
                "peripherals": get_peripherals(),
                **slow_raw,
            }
            payload = build_report_payload(agent_id, raw, hardware_uuid, full=full)
            result = send_report(
                payload,
                max_retries=None if full else config.LIGHT_MAX_RETRIES,
            )

            if result:
                # Only now is it safe to remember the peripheral state.
                _save_peripheral_snapshot(raw["peripherals"])

                if full:
                    last_full_ok = time.monotonic()

                logger.info(
                    "Synced OK (%s) | computer_id=%s | status=%s",
                    "full" if full else "light",
                    result.get("id"),
                    result.get("status"),
                )
                if result.get("pending_shutdown"):
                    trigger_shutdown(agent_id)

        except Exception:
            logger.exception("Unexpected error during collection/report cycle")

        elapsed = time.monotonic() - cycle_start
        time.sleep(max(0, config.FAST_REPORT_INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    try:
        run_forever()
    except KeyboardInterrupt:
        logger.info("Agent stopped by user.")