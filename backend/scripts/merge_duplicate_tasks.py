"""
One-time FIX for the "Run (OS) updates" / "Run (OS)updates" duplicate
task (a spacing typo created two separate rows in maintenance_tasks at
some point, which is why it appeared twice on both the biweekly page
and the printed Excel).

This does NOT delete any completion history:
  - Any maintenance_log rows pointing at the duplicate task get
    reassigned to point at the canonical task instead.
  - If a computer already has a log for the canonical task in the same
    period (the rare case where someone ticked both variants), we keep
    whichever one is completed (or the more recently completed one),
    and drop only the now-redundant duplicate row for that one
    computer+period - never touching any other computer's data.
  - Only after every log has been moved is the now-empty duplicate
    task row deleted.

Run once from backend/:  python -m scripts.merge_duplicate_tasks
"""

from app.db.database import SessionLocal
from app.models.maintenance_log import MaintenanceLog
from app.models.maintenance_task import MaintenanceTask

CANONICAL_NAME = "Run (OS) updates"       # the spelling seed_maintenance_tasks.py uses
DUPLICATE_NAME = "Run (OS)updates"        # the stray variant found in the DB


def run():
    db = SessionLocal()
    try:
        canonical = db.query(MaintenanceTask).filter(MaintenanceTask.name == CANONICAL_NAME).first()
        duplicate = db.query(MaintenanceTask).filter(MaintenanceTask.name == DUPLICATE_NAME).first()

        if not duplicate:
            print(f"No task named {DUPLICATE_NAME!r} found - nothing to do.")
            return
        if not canonical:
            print(f"No canonical task named {CANONICAL_NAME!r} found - renaming the "
                  f"duplicate instead of merging, since there's nothing to merge into.")
            duplicate.name = CANONICAL_NAME
            db.commit()
            print("Renamed. Done.")
            return

        dup_logs = db.query(MaintenanceLog).filter(MaintenanceLog.maintenance_task_id == duplicate.id).all()
        moved, merged_conflicts = 0, 0

        for log in dup_logs:
            existing = (
                db.query(MaintenanceLog)
                .filter(
                    MaintenanceLog.computer_id == log.computer_id,
                    MaintenanceLog.maintenance_task_id == canonical.id,
                    MaintenanceLog.period_label == log.period_label,
                )
                .first()
            )
            if existing is None:
                # No conflict - just repoint this log at the canonical task.
                log.maintenance_task_id = canonical.id
                moved += 1
                continue

            # Both variants were ticked for the same computer+period.
            # Keep whichever is completed (prefer the more recently
            # completed one if both are), drop the other - only for
            # this one computer+period, nothing else is touched.
            keep_existing = existing.completed and (
                not log.completed or (existing.completed_at or 0) >= (log.completed_at or 0)
            )
            if keep_existing:
                db.delete(log)
            else:
                existing.completed = log.completed
                existing.completed_by = log.completed_by
                existing.completed_at = log.completed_at
                db.delete(log)
            merged_conflicts += 1

        db.flush()
        db.delete(duplicate)
        db.commit()

        print(f"Moved {moved} log(s) to the canonical task.")
        print(f"Resolved {merged_conflicts} conflicting duplicate log(s).")
        print(f"Deleted the duplicate task row ({DUPLICATE_NAME!r}).")
        print("Done - only one 'Run (OS) updates' task remains.")
    finally:
        db.close()


if __name__ == "__main__":
    run()