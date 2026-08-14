"""
Business logic for the preventive-maintenance checklist module
(the digitized version of the Excel master list).
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.computer import Computer
from app.models.maintenance_log import MaintenanceLog
from app.models.maintenance_task import MaintenanceTask


def list_tasks(
    db: Session,
    frequency: str | None = None,
    active_only: bool = True,
) -> list[MaintenanceTask]:
    query = db.query(MaintenanceTask)

    if active_only:
        query = query.filter(MaintenanceTask.is_active.is_(True))
    if frequency:
        query = query.filter(MaintenanceTask.default_frequency == frequency)

    return query.order_by(MaintenanceTask.id).all()


def get_checklist(
    db: Session,
    computer_id: int,
    period_label: str,
    frequency: str | None = None,
) -> list[dict]:
    """
    Every active task (optionally filtered to one frequency) paired
    with whatever log row already exists for
    (computer, task, period) - or a blank "not completed yet" entry
    if the box has never been touched for this period.
    """
    tasks = list_tasks(db, frequency=frequency)

    logs = (
        db.query(MaintenanceLog)
        .filter(
            MaintenanceLog.computer_id == computer_id,
            MaintenanceLog.period_label == period_label,
        )
        .all()
    )
    logs_by_task = {log.maintenance_task_id: log for log in logs}

    checklist = []
    for task in tasks:
        log = logs_by_task.get(task.id)
        checklist.append({
            "task_id": task.id,
            "task_name": task.name,
            "frequency": task.default_frequency,
            "responsible_person": task.responsible_person,
            "period_label": period_label,
            "log_id": log.id if log else None,
            "completed": log.completed if log else False,
            "completed_by": log.completed_by if log else None,
            "completed_at": log.completed_at if log else None,
            "notes": log.notes if log else None,
        })

    return checklist


def toggle_maintenance_log(
    db: Session,
    computer_id: int,
    maintenance_task_id: int,
    period_label: str,
    completed: bool,
    completed_by: str | None = None,
    notes: str | None = None,
) -> MaintenanceLog:
    """
    Upserts the single row representing this task's tick/untick state
    for this computer, for this period.

    - Ticking sets completed=True and stamps completed_at/completed_by.
    - Unticking sets completed=False and clears completed_at.
    - The row is never deleted, so the "who last touched this" trail
      survives a box being unticked and re-ticked.
    """
    if not db.query(Computer.id).filter(Computer.id == computer_id).first():
        raise ValueError(f"Computer {computer_id} not found")

    if not db.query(MaintenanceTask.id).filter(MaintenanceTask.id == maintenance_task_id).first():
        raise ValueError(f"Maintenance task {maintenance_task_id} not found")

    log = (
        db.query(MaintenanceLog)
        .filter(
            MaintenanceLog.computer_id == computer_id,
            MaintenanceLog.maintenance_task_id == maintenance_task_id,
            MaintenanceLog.period_label == period_label,
        )
        .first()
    )

    if not log:
        log = MaintenanceLog(
            computer_id=computer_id,
            maintenance_task_id=maintenance_task_id,
            period_label=period_label,
        )
        db.add(log)

    log.completed = completed
    log.completed_by = completed_by
    if notes is not None:
        log.notes = notes
    log.completed_at = datetime.now(timezone.utc) if completed else None

    db.commit()
    db.refresh(log)
    return log


def get_computer_maintenance_view(
    db: Session,
    computer_id: int,
    period_label: str,
    frequency: str | None = None,
) -> dict | None:
    computer = db.query(Computer).filter(Computer.id == computer_id).first()
    if not computer:
        return None

    return {
        "computer_id": computer.id,
        "s_no": computer.s_no,
        "hostname": computer.hostname,
        "lab_section": computer.lab_section,
        "cpu_model": computer.cpu_model,
        "ram_total_gb": computer.ram_total_gb,
        "disk_total_gb": computer.disk_total_gb,
        "checklist": get_checklist(db, computer_id, period_label, frequency),
    }


def list_computers_for_maintenance(db: Session) -> list[Computer]:
    """All enrolled PCs, ordered the way the master list is ordered."""
    return (
        db.query(Computer)
        .order_by(Computer.s_no.asc().nulls_last(), Computer.hostname.asc())
        .all()
    )