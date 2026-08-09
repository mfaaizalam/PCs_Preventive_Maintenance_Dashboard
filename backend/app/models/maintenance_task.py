from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import MaintenanceFrequency
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.maintenance_log import MaintenanceLog


class MaintenanceTask(Base, TimestampMixin):
    __tablename__ = "maintenance_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    default_frequency: Mapped[MaintenanceFrequency] = mapped_column(
        String(20),
        default=MaintenanceFrequency.BIWEEKLY,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(
        back_populates="maintenance_task",
        cascade="all, delete-orphan",
    )
