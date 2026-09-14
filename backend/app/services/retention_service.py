"""
Data retention / cleanup.

The point of this module: on a free-tier Neon Postgres instance
(0.5 GB), the tables that grow WITHOUT bound over time are the
append-only ones - alerts, peripheral_events, hardware_change_log.
`computers`, `maintenance_log`, etc. are all upserted per PC and stay
roughly flat as the fleet size stays roughly flat (~60 PCs here).

This runs on a schedule from app/main.py (see _retention_sweep_loop)
and just deletes rows past their retention window.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.alert import Alert
from app.models.hardware_change_log import HardwareChangeLog
from app.models.peripheral_event import PeripheralEvent
from app.models.maintenance_log import MaintenanceLog

logger = logging.getLogger("app.retention")


def purge_old_alerts(db: Session) -> int:
    """
    Deletes alerts past ALERT_RETENTION_DAYS AND already resolved or
    acknowledged. An alert that's still open is NEVER deleted just
    because it's old.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.ALERT_RETENTION_DAYS)

    deleted = (
        db.query(Alert)
        .filter(
            Alert.created_at < cutoff,
            (Alert.resolved_at.isnot(None)) | (Alert.is_acknowledged.is_(True)),
        )
        .delete(synchronize_session=False)
    )
    if deleted:
        db.commit()
    return deleted


def purge_old_peripheral_events(db: Session) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(
        days=settings.PERIPHERAL_EVENT_RETENTION_DAYS
    )
    deleted = (
        db.query(PeripheralEvent)
        .filter(PeripheralEvent.occurred_at < cutoff)
        .delete(synchronize_session=False)
    )
    if deleted:
        db.commit()
    return deleted


def purge_old_hardware_change_logs(db: Session) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(
        days=settings.HARDWARE_CHANGE_LOG_RETENTION_DAYS
    )
    deleted = (
        db.query(HardwareChangeLog)
        .filter(HardwareChangeLog.changed_at < cutoff)
        .delete(synchronize_session=False)
    )
    if deleted:
        db.commit()
    return deleted

def purge_stale_maintenance_logs(db: Session) -> int:
    """
    Keeps only the CURRENT half-year's maintenance check data
    (Jan-Jun or Jul-Dec). The moment we cross into a new half,
    everything from before that half's start gets wiped - so at
    any time the table only ever holds the current ~6 months of
    checkmarks, not a year-round pile.
    """
    now = datetime.now(timezone.utc)
    if now.month <= 6:
        current_half_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    else:
        current_half_start = datetime(now.year, 7, 1, tzinfo=timezone.utc)

    deleted = (
        db.query(MaintenanceLog)
        .filter(MaintenanceLog.created_at < current_half_start)
        .delete(synchronize_session=False)
    )
    if deleted:
        db.commit()
    return deleted

def get_maintenance_retention_status(db: Session) -> dict:
    """
    Days left before the current half-year's maintenance_log rows get
    wiped by purge_stale_maintenance_logs(), plus how many rows are
    sitting in that window right now. Powers the "N days left - export
    now" countdown banner on the dashboard.
    """
    now = datetime.now(timezone.utc)
    if now.month <= 6:
        current_half_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
        current_half_label = f"{now.year}-H1"
        next_purge_date = datetime(now.year, 7, 1, tzinfo=timezone.utc)
    else:
        current_half_start = datetime(now.year, 7, 1, tzinfo=timezone.utc)
        current_half_label = f"{now.year}-H2"
        next_purge_date = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)

    affected_count = (
        db.query(MaintenanceLog)
        .filter(MaintenanceLog.created_at >= current_half_start)
        .count()
    )

    days_remaining = (next_purge_date - now).days

    return {
        "period_label": current_half_label,
        "next_purge_date": next_purge_date,
        "days_remaining": days_remaining,
        "affected_record_count": affected_count,
        "show_reminder": days_remaining <= settings.MAINTENANCE_LOG_REMINDER_DAYS,
    }

def run_retention_sweep(db: Session) -> dict:
    result = {
        "alerts_deleted": purge_old_alerts(db),
        "peripheral_events_deleted": purge_old_peripheral_events(db),
        "hardware_change_logs_deleted": purge_old_hardware_change_logs(db),
        "maintenance_logs_deleted": purge_stale_maintenance_logs(db),
    }
    if any(result.values()):
        logger.info("Retention sweep: %s", result)
    return result