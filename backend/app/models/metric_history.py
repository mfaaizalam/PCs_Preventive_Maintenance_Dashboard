from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.computer import Computer


class MetricHistory(Base):
    __tablename__ = "metrics_history"
    __table_args__ = (
        Index("ix_metrics_history_computer_recorded_at", "computer_id", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    cpu_usage_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    ram_usage_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    disk_usage_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    cpu_temperature_celsius: Mapped[float | None] = mapped_column(Float, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    computer: Mapped["Computer"] = relationship(back_populates="metrics_history")
