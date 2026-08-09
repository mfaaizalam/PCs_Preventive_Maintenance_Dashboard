from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import HardwareChangeType

if TYPE_CHECKING:
    from app.models.computer import Computer


class HardwareChangeLog(Base):
    __tablename__ = "hardware_change_log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    change_type: Mapped[HardwareChangeType] = mapped_column(String(20), nullable=False)

    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    entity_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)

    field_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    computer: Mapped["Computer"] = relationship(back_populates="hardware_change_logs")
