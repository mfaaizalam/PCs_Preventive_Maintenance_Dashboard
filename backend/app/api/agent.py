from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.agent import AgentReportPayload, DashboardOverviewResponse
from app.schemas.computer import ComputerResponse
from app.schemas.ram_slot import RamSlotResponse
from app.schemas.storage_device import StorageDeviceResponse
from app.schemas.installed_software import InstalledSoftwareResponse
from app.schemas.software_license import SoftwareLicenseResponse
from app.schemas.peripheral import PeripheralResponse
from app.schemas.peripheral_event import PeripheralEventResponse
from app.schemas.hardware_change_log import HardwareChangeLogResponse
from app.schemas.notification import HardwareNotificationResponse
from app.services import computer_service

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post(
    "/report",
    response_model=ComputerResponse,
    summary="Ingest a single agent check-in report",
)
def report(payload: AgentReportPayload, db: Session = Depends(get_db)):
    try:
        return computer_service.ingest_agent_report(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get(
    "/dashboard",
    response_model=DashboardOverviewResponse,
    summary="Get the aggregated dashboard overview",
)
def get_dashboard(db: Session = Depends(get_db)):
    return computer_service.get_dashboard_overview(db)


# Bell-icon hardware notifications (device-removed events, all PCs)

@router.get(
    "/notifications/hardware",
    response_model=list[HardwareNotificationResponse],
    summary="Get recent 'device removed' notifications across all PCs (bell icon feed)",
)
def get_hardware_notifications(
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    return computer_service.get_recent_hardware_notifications(db, hours=hours)


@router.get(
    "/computers/{agent_id}",
    response_model=ComputerResponse,
    summary="Get a single computer by agent_id",
)
def get_computer(agent_id: str, db: Session = Depends(get_db)):
    computer = computer_service.get_computer_by_agent_id(db, agent_id)
    if computer is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return computer


@router.get(
    "/computers/{agent_id}/ram-slots",
    response_model=list[RamSlotResponse],
    summary="Get RAM slots for a computer",
)
def get_ram_slots(agent_id: str, db: Session = Depends(get_db)):
    result = computer_service.get_ram_slots_by_agent_id(db, agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return result


@router.get(
    "/computers/{agent_id}/storage-devices",
    response_model=list[StorageDeviceResponse],
    summary="Get storage devices for a computer",
)
def get_storage_devices(agent_id: str, db: Session = Depends(get_db)):
    result = computer_service.get_storage_devices_by_agent_id(db, agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return result


@router.get(
    "/computers/{agent_id}/installed_software",
    response_model=list[InstalledSoftwareResponse],
    summary="Get installed software for a computer",
)
def get_installed_software(agent_id: str, db: Session = Depends(get_db)):
    result = computer_service.get_installed_software_by_agent_id(db, agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return result


@router.get(
    "/computers/{agent_id}/licenses",
    response_model=list[SoftwareLicenseResponse],
    summary="Get software licenses for a computer",
)
def get_software_licenses(agent_id: str, db: Session = Depends(get_db)):
    result = computer_service.get_software_licenses_by_agent_id(db, agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return result


@router.get(
    "/computers/{agent_id}/peripherals",
    response_model=list[PeripheralResponse],
    summary="Get peripherals for a computer",
)
def get_peripherals(agent_id: str, db: Session = Depends(get_db)):
    result = computer_service.get_peripherals_by_agent_id(db, agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return result


@router.get(
    "/computers/{agent_id}/peripheral-events",
    response_model=list[PeripheralEventResponse],
    summary="Get peripheral connect/disconnect history for a computer",
)
def get_peripheral_events(
    agent_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    result = computer_service.get_peripheral_events_by_agent_id(db, agent_id, limit=limit)
    if result is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return result


@router.get(
    "/computers/{agent_id}/hardware-changes",
    response_model=list[HardwareChangeLogResponse],
    summary="Get hardware/software/peripheral change history for a computer",
)
def get_hardware_changes(
    agent_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    result = computer_service.get_hardware_changes_by_agent_id(db, agent_id, limit=limit)
    if result is None:
        raise HTTPException(status_code=404, detail="Computer not found")
    return result