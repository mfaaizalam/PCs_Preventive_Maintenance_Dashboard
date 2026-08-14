from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.computer import Computer
    from app.models.maintenance_task import MaintenanceTask


class MaintenanceLog(Base, TimestampMixin):
    """
    One row per (computer, task, period) - this is the checkbox from
    the Excel sheet. The row is created the first time a task is
    touched for a given period and then just has `completed` flipped
    true/false from then on; it's never deleted, so unticking a box
    doesn't lose the record of who last touched it.
    """

    __tablename__ = "maintenance_log"
    __table_args__ = (
        UniqueConstraint(
            "computer_id",
            "maintenance_task_id",
            "period_label",
            name="uq_maintenance_log_computer_task_period",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    maintenance_task_id: Mapped[int] = mapped_column(
        ForeignKey("maintenance_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Encodes the specific occurrence being checked off, e.g.:
    #   biweekly:    "2026-08-W2"
    #   monthly:     "2026-08"
    #   half_yearly: "2026-H1"
    period_label: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Free-text - who actually ticked the box this time. Separate from
    # MaintenanceTask.responsible_person, which is just the default
    # role assignment.
    completed_by: Mapped[str | None] = mapped_column(String(200), nullable=True)

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    computer: Mapped["Computer"] = relationship(back_populates="maintenance_logs")
    maintenance_task: Mapped["MaintenanceTask"] = relationship(back_populates="maintenance_logs")