"""
One-off seed script for the maintenance task catalog, taken directly
from the Excel master list's biweekly/monthly/half-yearly columns.

Run once from backend/:  python -m scripts.seed_maintenance_tasks
Safe to run again later - skips any task name that already exists.
"""

from app.db.database import SessionLocal
from app.models.enums import MaintenanceFrequency
from app.models.maintenance_task import MaintenanceTask

TASKS = [
    # (name, frequency, responsible_person)
    ("Clean keyboards & mouse", MaintenanceFrequency.BIWEEKLY, "Lab Staff"),
    ("Check system boot-up", MaintenanceFrequency.BIWEEKLY, "Lab Staff"),
    ("Empty recycle bin", MaintenanceFrequency.BIWEEKLY, "IT-Support"),
    ("Run (OS) updates", MaintenanceFrequency.BIWEEKLY, "IT-Support"),
    ("Maintenance (any if required)", MaintenanceFrequency.MONTHLY, "IT Support"),
    ("Update/refresh OS", MaintenanceFrequency.HALF_YEARLY, "IT-Support"),
    ("Remove unused software/required software", MaintenanceFrequency.HALF_YEARLY, "IT-Support"),
    ("Review security passwords", MaintenanceFrequency.HALF_YEARLY, "IT-Manager"),
    ("Review software licenses/warranties", MaintenanceFrequency.HALF_YEARLY, "IT-Support"),
    ("Health check (RAM, HDD/SSD) - upgrade old components", MaintenanceFrequency.HALF_YEARLY, "IT-Manager"),
]


def run():
    db = SessionLocal()
    try:
        existing_names = {name for (name,) in db.query(MaintenanceTask.name).all()}
        added = 0

        for name, frequency, responsible_person in TASKS:
            if name in existing_names:
                continue
            db.add(
                MaintenanceTask(
                    name=name,
                    default_frequency=frequency,
                    responsible_person=responsible_person,
                )
            )
            added += 1

        db.commit()
        print(f"Seeded {added} new task(s), {len(TASKS) - added} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()