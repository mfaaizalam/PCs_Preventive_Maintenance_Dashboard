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


def run_retention_sweep(db: Session) -> dict:
    result = {
        "alerts_deleted": purge_old_alerts(db),
        "peripheral_events_deleted": purge_old_peripheral_events(db),
        "hardware_change_logs_deleted": purge_old_hardware_change_logs(db),
    }
    if any(result.values()):
        logger.info("Retention sweep: %s", result)
    return result