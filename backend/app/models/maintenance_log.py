from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.maintenance_asset import MaintenanceAsset
    from app.models.maintenance_task import MaintenanceTask
    from app.models.user import User


class MaintenanceLog(Base):
    __tablename__ = "maintenance_log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    maintenance_asset_id: Mapped[int] = mapped_column(
        ForeignKey("maintenance_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    maintenance_task_id: Mapped[int] = mapped_column(
        ForeignKey("maintenance_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    period_label: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Cycle label such as W1, W2, Month-1, etc.",
    )

    responsible_person: Mapped[str | None] = mapped_column(String(200), nullable=True)

    completed_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    maintenance_asset: Mapped["MaintenanceAsset"] = relationship(
        back_populates="maintenance_logs",
    )
    maintenance_task: Mapped["MaintenanceTask"] = relationship(
        back_populates="maintenance_logs",
    )
    completed_by: Mapped["User | None"] = relationship(back_populates="maintenance_logs")
