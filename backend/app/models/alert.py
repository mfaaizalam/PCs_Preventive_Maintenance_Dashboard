from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import AlertSeverity, AlertType

if TYPE_CHECKING:
    from app.models.computer import Computer
    from app.models.user import User


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int | None] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    alert_type: Mapped[AlertType] = mapped_column(String(20), nullable=False)

    severity: Mapped[AlertSeverity] = mapped_column(String(20), nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    source: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    acknowledged_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    computer: Mapped["Computer | None"] = relationship(back_populates="alerts")
    acknowledged_by: Mapped["User | None"] = relationship(
        back_populates="acknowledged_alerts",
        foreign_keys=[acknowledged_by_id],
    )
