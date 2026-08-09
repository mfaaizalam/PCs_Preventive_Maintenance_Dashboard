from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.computer import Computer


class RamSlot(Base, TimestampMixin):
    __tablename__ = "ram_slots"
    __table_args__ = (
        UniqueConstraint("computer_id", "slot_number", name="uq_ram_slots_computer_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    slot_number: Mapped[int] = mapped_column(Integer, nullable=False)

    capacity_gb: Mapped[float | None] = mapped_column(Float, nullable=True)

    manufacturer: Mapped[str | None] = mapped_column(String(100), nullable=True)

    speed_mhz: Mapped[int | None] = mapped_column(Integer, nullable=True)

    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    computer: Mapped["Computer"] = relationship(back_populates="ram_slots")
