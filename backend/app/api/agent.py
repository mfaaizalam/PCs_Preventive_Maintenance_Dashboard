from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.agent import AgentReportPayload, DashboardOverviewResponse
from app.schemas.computer import ComputerResponse
from app.services import computer_service

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