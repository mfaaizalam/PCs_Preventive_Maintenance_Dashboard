"""
Business logic for ingesting agent check-in reports and building
the dashboard overview. Called by app/api/agent.py.
"""

import re
from datetime import datetime, timedelta, timezone
from app.models.storage_device import StorageDevice
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.ram_slot import RamSlot
from app.models.alert import Alert
from app.models.computer import Computer
from app.models.enums import (
    AlertSeverity,
    AlertType,
    ComputerStatus,
    HardwareChangeType,
    PeripheralEventType,
)
from app.models.hardware_change_log import HardwareChangeLog
from app.models.installed_software import InstalledSoftware
from app.models.peripheral import Peripheral
from app.models.peripheral_event import PeripheralEvent
from app.models.ram_slot import RamSlot
from app.models.software_license import SoftwareLicense
from app.models.storage_device import StorageDevice
from app.schemas.agent import AgentReportPayload, DashboardOverviewResponse
from app.schemas.alert import AlertSummaryResponse
from app.schemas.computer import ComputerSummaryResponse
from app.schemas.notification import HardwareEventBrief, HardwareNotificationResponse
from app.models.peripheral_event import PeripheralEvent
# ------------------------------------------------------------------
# HARDWARE NOTIFICATION WINDOWS
# ------------------------------------------------------------------

# How far back a PC card's "recent hardware activity" list looks.
HARDWARE_ACTIVITY_CARD_DAYS = 3
# How many events to embed per PC in the dashboard overview payload.
HARDWARE_ACTIVITY_CARD_LIMIT = 5
# How far back the bell notification feed looks by default.
HARDWARE_NOTIFICATION_DEFAULT_HOURS = 24

# device_type -> human label. Falls back to a title-cased version of
# the raw string (e.g. "usb_storage" -> "Usb Storage") for anything
# not listed here, so new peripheral types never render blank.
DEVICE_TYPE_LABELS = {
    "mouse": "Mouse",
    "keyboard": "Keyboard",
    "touchpad": "Touchpad",
    "monitor": "Monitor",
    "printer": "Printer",
    "physical_printer": "Printer",
    "virtual_printer": "Virtual Printer",
    "usb_storage": "USB Storage",
    "webcam": "Webcam",
    "headset": "Headset",
    "docking_station": "Docking Station",
    "other": "Device",
}


def _device_label(device_type: str | None) -> str:
    if not device_type:
        return "Device"
    return DEVICE_TYPE_LABELS.get(device_type.lower(), device_type.replace("_", " ").title())


def _hardware_event_message(device_type: str | None, event_type: PeripheralEventType) -> str:
    label = _device_label(device_type)
    if event_type == PeripheralEventType.DISCONNECTED:
        return f"{label} removed"
    return f"{label} connected"
# ------------------------------------------------------------------
# THRESHOLDS
# ------------------------------------------------------------------

CPU_WARNING = 80
CPU_CRITICAL = 95
RAM_WARNING = 85
RAM_CRITICAL = 95
DISK_WARNING = 85
DISK_CRITICAL = 95

TRACKED_COMPUTER_FIELDS = {
    "hostname": HardwareChangeType.OTHER,
    "ip_address": HardwareChangeType.NETWORK,
    "cpu_model": HardwareChangeType.CPU,
    "os_name": HardwareChangeType.SOFTWARE,
    "os_version": HardwareChangeType.SOFTWARE,
}

DIRECT_ASSIGN_FIELDS = [
    "asset_id",
    "hardware_uuid",
    "lab_name",
    "lab_section",
    "cpu_usage_percent",
    "cpu_temperature_celsius",
    "ram_total_gb",
    "ram_usage_percent",
    "disk_total_gb",
    "disk_usage_percent",
    "uptime_seconds",
]

# ------------------------------------------------------------------
# AUTO LAB / PC-NUMBER IDENTIFICATION
# ------------------------------------------------------------------
# Best-effort parse of "<SECTION>-...-<NUMBER>" out of the hostname
# the agent reports, e.g.:
#   "CAED-LAB-14"  -> section="CAED",   number="14"
#   "CADCAM-05"    -> section="CADCAM", number="05"
#   "OFFICE-PC-3"  -> section="OFFICE", number="3"
#   "CAED14"       -> section="CAED",   number="14"
# Used so a PC is filed under its real lab the moment its agent
# checks in, instead of relying on someone hand-editing
# LAB_NAME/LAB_SECTION in agent/config.py or using the manual "Add
# PC" form (removed in Module 2).
_HOSTNAME_LAB_PATTERNS = [
    re.compile(r"^(?P<section>[A-Za-z]+(?:/[A-Za-z]+)*)[-_](?:[A-Za-z]+[-_])?(?P<number>\d{1,4})$"),
    re.compile(r"^(?P<section>[A-Za-z]+(?:/[A-Za-z]+)*)(?P<number>\d{1,4})$"),
]


def _derive_lab_from_hostname(hostname: str) -> tuple[str | None, str | None]:
    """
    Returns (lab_section, pc_number) parsed from the hostname, or
    (None, None) if the hostname doesn't match a recognizable shape.
    lab_section is uppercased so "caed-lab-3" and "CAED-LAB-9" group
    together under the same Category.
    """
    if not hostname:
        return None, None
    candidate = hostname.strip()
    for pattern in _HOSTNAME_LAB_PATTERNS:
        match = pattern.match(candidate)
        if match:
            return match.group("section").upper(), match.group("number")
    return None, None


def _apply_auto_lab_identity(db: Session, computer: Computer) -> None:
    """
    Fills in lab_section / asset_id (PC number tag) from the hostname
    when they're still empty, so the PC shows up under its real lab
    in Categories/Dashboard/Maintenance instead of "Unassigned". Never
    overwrites a value that's already set (explicit agent config or a
    prior fill both win).
    """
    if computer.lab_section and computer.asset_id:
        return

    derived_section, derived_number = _derive_lab_from_hostname(computer.hostname)

    if not computer.lab_section and derived_section:
        computer.lab_section = derived_section

    if not computer.asset_id and derived_number:
        candidate_asset_id = (
            f"{derived_section}-{derived_number}" if derived_section else derived_number
        )
        clash = (
            db.query(Computer.id)
            .filter(Computer.asset_id == candidate_asset_id, Computer.id != computer.id)
            .first()
        )
        if not clash:
            computer.asset_id = candidate_asset_id


def _compute_status(
    cpu: float | None,
    ram: float | None,
    disk: float | None,
) -> ComputerStatus:
    metrics = [m for m in (cpu, ram, disk) if m is not None]

    if not metrics:
        return ComputerStatus.UNKNOWN

    if (cpu is not None and cpu >= CPU_CRITICAL) or \
       (ram is not None and ram >= RAM_CRITICAL) or \
       (disk is not None and disk >= DISK_CRITICAL):
        return ComputerStatus.CRITICAL

    if (cpu is not None and cpu >= CPU_WARNING) or \
       (ram is not None and ram >= RAM_WARNING) or \
       (disk is not None and disk >= DISK_WARNING):
        return ComputerStatus.ATTENTION

    return ComputerStatus.HEALTHY


def delete_computer(db: Session, computer_id: int) -> bool:
    """Removes a PC (and, via cascade, its maintenance/alert/history rows)."""
    computer = db.query(Computer).filter(Computer.id == computer_id).first()
    if not computer:
        return False
    db.delete(computer)
    db.commit()
    return True


def get_computer_by_agent_id(db: Session, agent_id: str) -> Computer | None:
    return db.query(Computer).filter(Computer.agent_id == agent_id).first()


def ingest_agent_report(db: Session, payload: AgentReportPayload) -> Computer:
    """
    Create or update a Computer row plus all related hardware /
    software / peripheral data from a single agent check-in payload.
    """

    now = datetime.now(timezone.utc)

    computer = get_computer_by_agent_id(db, payload.agent_id)

    # agent_id.txt can get wiped/regenerated (re-run, reinstall, moved
    # folder, etc.). If that happens, fall back to matching the same
    # physical PC by hardware_uuid or hostname instead of trying to
    # insert a second row that collides on those unique constraints.
    if not computer and payload.hardware_uuid:
        computer = (
            db.query(Computer)
            .filter(Computer.hardware_uuid == payload.hardware_uuid)
            .first()
        )

    if not computer:
        computer = (
            db.query(Computer)
            .filter(Computer.hostname == payload.hostname)
            .first()
        )

    is_new = computer is None

    # The unique constraint on hostname means two different physical
    # PCs (different agent_id/hardware_uuid) can't both be named the
    # same thing. That used to surface as a raw 500 from a bare
    # IntegrityError deep in db.flush(); catch it here instead with a
    # message that says which two computer rows actually collide, so
    # whoever's reading the API response (or server log) can go
    # rename/remove one of them instead of guessing.
    conflict = (
        db.query(Computer)
        .filter(Computer.hostname == payload.hostname)
        .filter(Computer.id != computer.id if computer is not None else True)
        .first()
    )
    if conflict:
        raise ValueError(
            f"Hostname '{payload.hostname}' is already used by computer id={conflict.id} "
            f"(agent_id='{conflict.agent_id}'). This report is from agent_id="
            f"'{payload.agent_id}'"
            + (f", matched to existing computer id={computer.id}" if computer is not None else "")
            + ". Rename the PC in Windows, or delete the stale duplicate via "
            "DELETE /api/computers/{id}, then have the agent report again."
        )

    if is_new:
        computer = Computer(agent_id=payload.agent_id, hostname=payload.hostname)
        db.add(computer)
    elif computer.agent_id != payload.agent_id:
        # Same PC, new agent_id - adopt it rather than erroring out.
        computer.agent_id = payload.agent_id

    # ---- track changes on a few "interesting" fields ----
    changes: list[tuple[str, HardwareChangeType, str | None, str | None]] = []

    for field, change_type in TRACKED_COMPUTER_FIELDS.items():
        new_value = getattr(payload, field, None)
        if new_value is None:
            continue
        old_value = getattr(computer, field, None)
        if not is_new and old_value != new_value:
            changes.append((field, change_type, old_value, new_value))
        setattr(computer, field, new_value)

    # ---- overwrite the rest of the simple fields ----
    for field in DIRECT_ASSIGN_FIELDS:
        value = getattr(payload, field, None)
        if value is not None:
            setattr(computer, field, value)

    computer.is_online = payload.is_online
    computer.last_seen = payload.reported_at or now
    computer.status = (
        _compute_status(
            computer.cpu_usage_percent,
            computer.ram_usage_percent,
            computer.disk_usage_percent,
        )
        if computer.is_online
        else ComputerStatus.OFFLINE
    )

    # flush so computer.id exists for child rows / logs below
    db.flush()

    # ---- auto-identify lab section + PC number from hostname ----
    _apply_auto_lab_identity(db, computer)

    for field, change_type, old_value, new_value in changes:
        db.add(
            HardwareChangeLog(
                computer_id=computer.id,
                change_type=change_type,
                entity_type="computer",
                field_name=field,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None,
            )
        )

    _upsert_ram_slots(db, computer, payload.ram_slots)
    _upsert_storage_devices(db, computer, payload.storage_devices)
    _upsert_peripherals(db, computer, payload.peripherals)
    _record_peripheral_events(db, computer, payload.peripheral_events)
    _upsert_software_licenses(db, computer, payload.software_licenses)
    _upsert_installed_software(db, computer, payload.installed_software)
    _generate_threshold_alert(db, computer)

    db.commit()
    db.refresh(computer)
    return computer


# ------------------------------------------------------------------
# CHILD-TABLE UPSERT HELPERS
# ------------------------------------------------------------------

def _upsert_ram_slots(db: Session, computer: Computer, items) -> None:
    existing = {row.slot_number: row for row in computer.ram_slots}
    incoming_slots = set()

    for item in items:
        incoming_slots.add(item.slot_number)
        data = item.model_dump()
        row = existing.get(item.slot_number)

        if row:
            for key, value in data.items():
                setattr(row, key, value)
        else:
            db.add(RamSlot(computer_id=computer.id, **data))

    if items:
        for slot_number, row in existing.items():
            if slot_number not in incoming_slots:
                db.delete(row)


def _upsert_storage_devices(db: Session, computer: Computer, items) -> None:
    existing = {row.device_identifier: row for row in computer.storage_devices}
    incoming_ids = set()

    for item in items:
        incoming_ids.add(item.device_identifier)
        data = item.model_dump()
        row = existing.get(item.device_identifier)

        if row:
            for key, value in data.items():
                setattr(row, key, value)
        else:
            db.add(StorageDevice(computer_id=computer.id, **data))

    if items:
        for device_id, row in existing.items():
            if device_id not in incoming_ids:
                db.delete(row)


def _upsert_peripherals(db: Session, computer: Computer, items) -> None:
    existing = {row.device_key: row for row in computer.peripherals}
    incoming_keys = set()
    now = datetime.now(timezone.utc)

    for item in items:
        incoming_keys.add(item.device_key)
        data = item.model_dump()
        data.setdefault("last_seen_at", now)
        row = existing.get(item.device_key)

        if row:
            old_status = row.status
            for key, value in data.items():
                setattr(row, key, value)

            if old_status != row.status:
                _log_peripheral_status_change(db, computer, row, old_status, row.status)
        else:
            db.add(Peripheral(computer_id=computer.id, **data))

    # anything previously seen but not reported this round -> missing
    if items:
        for device_key, row in existing.items():
            if device_key not in incoming_keys and row.status != "missing":
                old_status = row.status
                row.status = "missing"
                _log_peripheral_status_change(db, computer, row, old_status, "missing")
def _log_peripheral_status_change(
    db: Session,
    computer: Computer,
    peripheral: Peripheral,
    old_status,
    new_status,
) -> None:
    """
    Records both an audit-trail row (hardware_change_log) and a
    connect/disconnect row (peripheral_events) whenever a peripheral's
    status actually changes - e.g. a USB mouse unplugged or reconnected.
    """
    db.add(
        HardwareChangeLog(
            computer_id=computer.id,
            change_type=HardwareChangeType.PERIPHERAL,
            entity_type="peripheral",
            entity_identifier=peripheral.device_key,
            field_name="status",
            old_value=str(old_status) if old_status else None,
            new_value=str(new_status),
        )
    )

    event_type = (
        PeripheralEventType.DISCONNECTED
        if new_status in ("missing", "disconnected")
        else PeripheralEventType.CONNECTED
    )

    db.add(
        PeripheralEvent(
            computer_id=computer.id,
            peripheral_id=peripheral.id,
            event_type=event_type,
            device_type=peripheral.device_type,
            device_key=peripheral.device_key,
            vendor_id=peripheral.vendor_id,
            product_id=peripheral.product_id,
            serial_number=peripheral.serial_number,
            port_path=peripheral.port_path,
            details=f"status changed from {old_status} to {new_status}",
        )
    )
def _record_peripheral_events(db: Session, computer: Computer, events) -> None:
    peripherals_by_key = {row.device_key: row for row in computer.peripherals}

    for event in events:
        data = event.model_dump()
        peripheral = peripherals_by_key.get(data.get("device_key"))
        db.add(
            PeripheralEvent(
                computer_id=computer.id,
                peripheral_id=peripheral.id if peripheral else None,
                **data,
            )
        )


def _upsert_software_licenses(db: Session, computer: Computer, items) -> None:
    existing = {row.product_name: row for row in computer.software_licenses}

    for item in items:
        data = item.model_dump()
        row = existing.get(item.product_name)

        if row:
            for key, value in data.items():
                setattr(row, key, value)
        else:
            db.add(SoftwareLicense(computer_id=computer.id, **data))


def _upsert_installed_software(db: Session, computer: Computer, items) -> None:
    existing = {
        (row.name, row.publisher): row for row in computer.installed_software
    }

    for item in items:
        data = item.model_dump()
        row = existing.get((item.name, item.publisher))

        if row:
            for key, value in data.items():
                setattr(row, key, value)
        else:
            db.add(InstalledSoftware(computer_id=computer.id, **data))


def _generate_threshold_alert(db: Session, computer: Computer) -> None:
    if computer.status not in (ComputerStatus.CRITICAL, ComputerStatus.ATTENTION):
        return

    severity = (
        AlertSeverity.CRITICAL
        if computer.status == ComputerStatus.CRITICAL
        else AlertSeverity.WARNING
    )
    message = (
        f"{computer.hostname} is {computer.status.value}: "
        f"CPU {computer.cpu_usage_percent}%, "
        f"RAM {computer.ram_usage_percent}%, "
        f"Disk {computer.disk_usage_percent}%"
    )

    existing = (
        db.query(Alert)
        .filter(
            Alert.computer_id == computer.id,
            Alert.alert_type == AlertType.PERFORMANCE,
            Alert.is_acknowledged.is_(False),
            Alert.resolved_at.is_(None),
        )
        .first()
    )

    if existing:
        existing.severity = severity
        existing.message = message
    else:
        db.add(
            Alert(
                computer_id=computer.id,
                alert_type=AlertType.PERFORMANCE,
                severity=severity,
                title=f"{computer.hostname} resource usage {computer.status.value}",
                message=message,
                source="agent",
            )
        )


# ------------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------------

def _recent_hardware_events_by_computer(
    db: Session,
    computer_ids: list[int],
    days: int = HARDWARE_ACTIVITY_CARD_DAYS,
    per_computer_limit: int = HARDWARE_ACTIVITY_CARD_LIMIT,
) -> dict[int, list[HardwareEventBrief]]:
    """
    One bulk query for every computer's recent peripheral connect/
    disconnect activity (instead of one request per PC card). Returns
    at most `per_computer_limit` most-recent events per computer,
    newest first, from the last `days` days.
    """
    if not computer_ids:
        return {}

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.query(PeripheralEvent)
        .filter(
            PeripheralEvent.computer_id.in_(computer_ids),
            PeripheralEvent.occurred_at >= cutoff,
        )
        .order_by(PeripheralEvent.occurred_at.desc())
        .all()
    )

    grouped: dict[int, list[HardwareEventBrief]] = {}
    for row in rows:
        bucket = grouped.setdefault(row.computer_id, [])
        if len(bucket) >= per_computer_limit:
            continue
        bucket.append(
            HardwareEventBrief(
                event_type=row.event_type,
                device_type=row.device_type,
                message=_hardware_event_message(row.device_type, row.event_type),
                occurred_at=row.occurred_at,
            )
        )
    return grouped


def get_dashboard_overview(db: Session) -> DashboardOverviewResponse:
    computers = db.query(Computer).order_by(Computer.hostname).all()

    healthy = sum(1 for c in computers if c.status == ComputerStatus.HEALTHY)
    attention = sum(1 for c in computers if c.status == ComputerStatus.ATTENTION)
    critical = sum(1 for c in computers if c.status == ComputerStatus.CRITICAL)
    offline = sum(1 for c in computers if not c.is_online)

    active_alert_count = (
        db.query(Alert)
        .filter(Alert.is_acknowledged.is_(False), Alert.resolved_at.is_(None))
        .count()
    )

    recent_alerts = (
        db.query(Alert)
        .filter(Alert.resolved_at.is_(None))
        .order_by(Alert.created_at.desc())
        .limit(10)
        .all()
    )

    hardware_events_by_computer = _recent_hardware_events_by_computer(
        db, [c.id for c in computers]
    )

    computer_summaries = []
    for c in computers:
        summary = ComputerSummaryResponse.model_validate(c)
        summary = summary.model_copy(
            update={"recent_hardware_events": hardware_events_by_computer.get(c.id, [])}
        )
        computer_summaries.append(summary)

    return DashboardOverviewResponse(
        total_pcs=len(computers),
        healthy_count=healthy,
        attention_count=attention,
        critical_count=critical,
        offline_count=offline,
        active_alert_count=active_alert_count,
        last_refresh_at=datetime.now(timezone.utc),
        computers=computer_summaries,
        recent_alerts=[AlertSummaryResponse.model_validate(a) for a in recent_alerts],
    )


def get_recent_hardware_notifications(
    db: Session,
    hours: int = HARDWARE_NOTIFICATION_DEFAULT_HOURS,
) -> list[HardwareNotificationResponse]:
    """
    Bell-icon feed: every "device removed" event (disconnected) across
    all PCs in the last `hours` hours, newest first. Built from the
    existing peripheral_events table joined to computers.hostname -
    no new table, matches HardwareChangeLog/PeripheralEvent already
    written by _log_peripheral_status_change on each agent check-in.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    rows = (
        db.query(PeripheralEvent, Computer.hostname, Computer.agent_id)
        .join(Computer, Computer.id == PeripheralEvent.computer_id)
        .filter(
            PeripheralEvent.event_type == PeripheralEventType.DISCONNECTED,
            PeripheralEvent.occurred_at >= cutoff,
        )
        .order_by(PeripheralEvent.occurred_at.desc())
        .all()
    )

    return [
        HardwareNotificationResponse(
            id=event.id,
            computer_id=event.computer_id,
            agent_id=agent_id,
            hostname=hostname,
            device_type=event.device_type,
            message=_hardware_event_message(event.device_type, event.event_type),
            occurred_at=event.occurred_at,
        )
        for event, hostname, agent_id in rows
    ]

def get_ram_slots_by_agent_id(db: Session, agent_id: str) -> list[RamSlot] | None:
    """
    Returns the RAM slots for the computer with this agent_id, or
    None if no computer with that agent_id exists (route turns that
    into a 404). Empty list means the computer exists but the agent
    hasn't reported any RAM slot data yet.
    """
    computer = get_computer_by_agent_id(db, agent_id)
    if computer is None:
        return None
    return computer.ram_slots

#  Storage Devices
def get_storage_devices_by_agent_id(db: Session, agent_id: str) -> list[StorageDevice] | None:
    """
    Returns the storage devices for the computer with this agent_id,
    or None if no computer with that agent_id exists (route turns
    that into a 404). Empty list means the computer exists but the
    agent hasn't reported any storage device data yet.
    """
    computer = get_computer_by_agent_id(db, agent_id)
    if computer is None:
        return None
    return computer.storage_devices
# Install software
def get_installed_software_by_agent_id(db: Session, agent_id: str) -> list[InstalledSoftware] | None:
    """
    Returns the installed-software inventory for the computer with
    this agent_id, or None if no computer with that agent_id exists
    (route turns that into a 404). Empty list means the computer
    exists but the agent hasn't reported any software inventory yet.
    """
    computer = get_computer_by_agent_id(db, agent_id)
    if computer is None:
        return None
    return computer.installed_software

# Software Licenses
def get_software_licenses_by_agent_id(db: Session, agent_id: str) -> list[SoftwareLicense] | None:
    """
    Returns the software licenses for the computer with this
    agent_id, or None if no computer with that agent_id exists
    (route turns that into a 404). Empty list means the computer
    exists but the agent hasn't reported any license data yet.
    """
    computer = get_computer_by_agent_id(db, agent_id)
    if computer is None:
        return None
    return computer.software_licenses
# Get Peripherals
def get_peripherals_by_agent_id(db: Session, agent_id: str) -> list[Peripheral] | None:
    """
    Returns the peripherals for the computer with this agent_id, or
    None if no computer with that agent_id exists (route turns that
    into a 404). Empty list means the computer exists but the agent
    hasn't reported any peripherals yet.
    """
    computer = get_computer_by_agent_id(db, agent_id)
    if computer is None:
        return None
    return computer.peripherals

# Peripheral _event
def get_peripheral_events_by_agent_id(
    db: Session,
    agent_id: str,
    limit: int = 100,
) -> list[PeripheralEvent] | None:
    """
    Returns the peripheral connect/disconnect history for the
    computer with this agent_id, most recent first, or None if no
    computer with that agent_id exists (route turns that into a
    404). Empty list means the computer exists but no peripheral
    events have been recorded yet. `limit` caps how many rows come
    back, since this table only grows over time (unlike the
    snapshot-style tables the other agent-data endpoints read from).
    """
    computer = get_computer_by_agent_id(db, agent_id)
    if computer is None:
        return None

    return (
        db.query(PeripheralEvent)
        .filter(PeripheralEvent.computer_id == computer.id)
        .order_by(PeripheralEvent.occurred_at.desc())
        .limit(limit)
        .all()
    )

# hardware_change_log

def get_hardware_changes_by_agent_id(
    db: Session,
    agent_id: str,
    limit: int = 100,
) -> list[HardwareChangeLog] | None:
    """
    Returns the hardware/software/peripheral change audit trail for
    the computer with this agent_id, most recent first, or None if
    no computer with that agent_id exists (route turns that into a
    404). Empty list means the computer exists but no changes have
    been recorded yet. `limit` caps how many rows come back, since
    this table only grows over time — same reasoning as
    get_peripheral_events_by_agent_id.
    """
    computer = get_computer_by_agent_id(db, agent_id)
    if computer is None:
        return None

    return (
        db.query(HardwareChangeLog)
        .filter(HardwareChangeLog.computer_id == computer.id)
        .order_by(HardwareChangeLog.changed_at.desc())
        .limit(limit)
        .all()
    )



def mark_stale_computers_offline(db: Session) -> list[Computer]:
    """
    Flips is_online=False (and status=OFFLINE) for any computer whose
    last_seen is older than OFFLINE_THRESHOLD_SECONDS. Returns the list
    of computers that were just flipped, so the caller can broadcast
    the change over the websocket.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(
        seconds=settings.OFFLINE_THRESHOLD_SECONDS
    )

    stale = (
        db.query(Computer)
        .filter(Computer.is_online.is_(True))
        .filter(
            (Computer.last_seen.is_(None)) | (Computer.last_seen < cutoff)
        )
        .all()
    )

    for computer in stale:
        computer.is_online = False
        computer.status = ComputerStatus.OFFLINE

    if stale:
        db.commit()

    return stale