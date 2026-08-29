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


def get_maintenance_summary(
    db: Session,
    frequency: str,
    period_label: str,
) -> dict:
    """
    Rolls the per-PC checklist up into one collective view for a
    frequency + period: overall completion, completion per task, and
    completion per lab section. Powers the checklist chart rather
    than the single-PC checklist table.
    """
    tasks = list_tasks(db, frequency=frequency)
    computers = list_computers_for_maintenance(db)

    logs = (
        db.query(MaintenanceLog)
        .join(MaintenanceTask, MaintenanceLog.maintenance_task_id == MaintenanceTask.id)
        .filter(
            MaintenanceLog.period_label == period_label,
            MaintenanceTask.default_frequency == frequency,
            MaintenanceLog.completed.is_(True),
        )
        .all()
    )
    completed_pairs = {(log.computer_id, log.maintenance_task_id) for log in logs}

    total_tasks = len(tasks)
    total_computers = len(computers)
    total_count = total_tasks * total_computers
    completed_count = sum(
        1
        for c in computers
        for t in tasks
        if (c.id, t.id) in completed_pairs
    )

    by_task = []
    for t in tasks:
        done = sum(1 for c in computers if (c.id, t.id) in completed_pairs)
        by_task.append({
            "task_id": t.id,
            "task_name": t.name,
            "completed_count": done,
            "total_count": total_computers,
            "percent": round((done / total_computers) * 100, 1) if total_computers else 0.0,
        })

    sections: dict[str, list[Computer]] = {}
    for c in computers:
        sections.setdefault(c.lab_section or "Unassigned", []).append(c)

    by_lab_section = []
    for section, section_computers in sorted(sections.items()):
        section_total = len(section_computers) * total_tasks
        section_done = sum(
            1
            for c in section_computers
            for t in tasks
            if (c.id, t.id) in completed_pairs
        )
        by_lab_section.append({
            "lab_section": section,
            "completed_count": section_done,
            "total_count": section_total,
            "percent": round((section_done / section_total) * 100, 1) if section_total else 0.0,
        })

    return {
        "frequency": frequency,
        "period_label": period_label,
        "total_computers": total_computers,
        "total_tasks": total_tasks,
        "completed_count": completed_count,
        "total_count": total_count,
        "percent": round((completed_count / total_count) * 100, 1) if total_count else 0.0,
        "by_task": by_task,
        "by_lab_section": by_lab_section,
    }


def list_computers_for_maintenance(db: Session) -> list[Computer]:
    """
    All enrolled, non-retired PCs, ordered the way the master list is
    ordered. Retired PCs are excluded so a dead/replaced PC stops
    appearing in the checklist and its Excel export on its own, with
    no manual delete needed.
    """
    return (
        db.query(Computer)
        .filter(Computer.is_retired.is_(False))
        .order_by(Computer.s_no.asc().nulls_last(), Computer.hostname.asc())
        .all()
    )