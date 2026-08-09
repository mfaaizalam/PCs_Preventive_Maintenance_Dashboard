from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import PeripheralEventType

if TYPE_CHECKING:
    from app.models.computer import Computer
    from app.models.peripheral import Peripheral


class PeripheralEvent(Base):
    __tablename__ = "peripheral_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    peripheral_id: Mapped[int | None] = mapped_column(
        ForeignKey("peripherals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    event_type: Mapped[PeripheralEventType] = mapped_column(String(20), nullable=False)

    device_type: Mapped[str | None] = mapped_column(String(30), nullable=True)

    device_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    vendor_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    product_id: Mapped[str | None] = mapped_column(String(20), nullable=True)

    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    port_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    computer: Mapped["Computer"] = relationship(back_populates="peripheral_events")
    peripheral: Mapped["Peripheral | None"] = relationship(back_populates="events")
