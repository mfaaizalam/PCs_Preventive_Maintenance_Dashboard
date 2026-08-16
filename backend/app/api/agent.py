from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from app.schemas.ram_slot import RamSlotResponse
from app.db.database import get_db
from app.schemas.agent import AgentReportPayload, DashboardOverviewResponse
from app.schemas.computer import ComputerResponse
from app.services import computer_service
from app.schemas.storage_device import StorageDeviceResponse
from app.schemas.installed_software import InstalledSoftwareResponse
from app.schemas.software_license import SoftwareLicenseResponse
from app.schemas.peripheral import PeripheralResponse
from app.schemas.peripheral_event import PeripheralEventResponse
from app.schemas.hardware_change_log import HardwareChangeLogResponse
router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post(
    "/report",
    response_model=ComputerResponse,
    status_code=status.HTTP_200_OK,
    summary="Receive a check-in report from a monitoring agent",
)
def submit_agent_report(
    payload: AgentReportPayload,
    db: Session = Depends(get_db),
):
    """
    Called by the agent on every check-in. Creates the computer on
    first contact, updates it and all related hardware / software /
    peripheral records on every call after that.
    """
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


@router.get(
    "/computers/{agent_id}",
    response_model=ComputerResponse,
    summary="Get a single computer's current state by its agent_id",
)
def get_computer(agent_id: str, db: Session = Depends(get_db)):
    computer = computer_service.get_computer_by_agent_id(db, agent_id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    return computer

# adding Ram_slot 

@router.get(
    "/computers/{agent_id}/ram-slots",
    response_model=list[RamSlotResponse],
)
def get_ram_slots(agent_id: str, db: Session = Depends(get_db)):
    ram_slots = computer_service.get_ram_slots_by_agent_id(db, agent_id)
    if ram_slots is None:
        raise HTTPException(
            status_code=404,
            detail=f"No computer found with agent_id '{agent_id}'",
        )
    return ram_slots


# Storage device route


@router.get(
    "/computers/{agent_id}/storage-devices",
    response_model=list[StorageDeviceResponse],
)
def get_storage_devices(agent_id: str, db: Session = Depends(get_db)):
    storage_devices = computer_service.get_storage_devices_by_agent_id(db, agent_id)
    if storage_devices is None:
        raise HTTPException(
            status_code=404,
            detail=f"No computer found with agent_id '{agent_id}'",
        )
    return storage_devices


# Install software

@router.get("/computers/{agent_id}/installed_software", response_model=list[InstalledSoftwareResponse],)
def get_installed_software(agent_id:str,db:Session=Depends(get_db)):
    install_software = computer_service.get_installed_software_by_agent_id(db,agent_id)
    if install_software is None:
        raise HTTPException(
                    status_code=404,
                    detail=f"No Installed Software found with agent_id '{agent_id}'",
                )
    return install_software



# Software & License Info

@router.get("/computers/{agent_id}/licenses", response_model=list[SoftwareLicenseResponse])
def get_software_licenses(agent_id: str, db: Session = Depends(get_db)):
    licenses = computer_service.get_software_licenses_by_agent_id(db, agent_id)
    if licenses is None:
        raise HTTPException(
            status_code=404,
            detail=f"No computer found with agent_id '{agent_id}'",
        )
    return licenses



# Connected Peripherals

@router.get("/computers/{agent_id}/peripherals", response_model=list[PeripheralResponse])
def get_peripherals(agent_id: str, db: Session = Depends(get_db)):
    peripherals = computer_service.get_peripherals_by_agent_id(db, agent_id)
    if peripherals is None:
        raise HTTPException(
            status_code=404,
            detail=f"No computer found with agent_id '{agent_id}'",
        )
    return peripherals



# Peripheral Connect / Disconnect History

@router.get("/computers/{agent_id}/peripheral-events", response_model=list[PeripheralEventResponse])
def get_peripheral_events(
    agent_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    events = computer_service.get_peripheral_events_by_agent_id(db, agent_id, limit=limit)
    if events is None:
        raise HTTPException(
            status_code=404,
            detail=f"No computer found with agent_id '{agent_id}'",
        )
    return events




# Hardware Change History

@router.get("/computers/{agent_id}/hardware-changes", response_model=list[HardwareChangeLogResponse])
def get_hardware_changes(
    agent_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    changes = computer_service.get_hardware_changes_by_agent_id(db, agent_id, limit=limit)
    if changes is None:
        raise HTTPException(
            status_code=404,
            detail=f"No computer found with agent_id '{agent_id}'",
        )
    return changes