from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import PeripheralStatus, PeripheralType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.computer import Computer
    from app.models.peripheral_event import PeripheralEvent


class Peripheral(Base, TimestampMixin):
    __tablename__ = "peripherals"
    __table_args__ = (
        UniqueConstraint(
            "computer_id",
            "device_key",
            name="uq_peripherals_computer_device_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    device_key: Mapped[str] = mapped_column(String(255), nullable=False)

    device_type: Mapped[PeripheralType] = mapped_column(
        String(30),
        nullable=False,
    )

    vendor_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    product_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    port_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    friendly_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    model: Mapped[str | None] = mapped_column(String(200), nullable=True)

    capacity_gb: Mapped[float | None] = mapped_column(Float, nullable=True)

    volume_label: Mapped[str | None] = mapped_column(String(100), nullable=True)

    descriptor: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[PeripheralStatus] = mapped_column(
        String(20),
        default=PeripheralStatus.DISCONNECTED,
        nullable=False,
    )

    is_expected: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    computer: Mapped["Computer"] = relationship(back_populates="peripherals")
    events: Mapped[list["PeripheralEvent"]] = relationship(
        back_populates="peripheral",
        cascade="all, delete-orphan",
    )
