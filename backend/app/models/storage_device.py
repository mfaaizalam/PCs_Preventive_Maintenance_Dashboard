from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import StorageDeviceType, StorageHealthStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.computer import Computer


class StorageDevice(Base, TimestampMixin):
    __tablename__ = "storage_devices"
    __table_args__ = (
        UniqueConstraint(
            "computer_id",
            "device_identifier",
            name="uq_storage_devices_computer_device",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    device_identifier: Mapped[str] = mapped_column(String(200), nullable=False)

    device_type: Mapped[StorageDeviceType] = mapped_column(
        String(20),
        default=StorageDeviceType.OTHER,
        nullable=False,
    )

    model: Mapped[str | None] = mapped_column(String(200), nullable=True)

    capacity_gb: Mapped[float | None] = mapped_column(Float, nullable=True)

    health_status: Mapped[StorageHealthStatus] = mapped_column(
        String(20),
        default=StorageHealthStatus.UNKNOWN,
        nullable=False,
    )

    smart_status: Mapped[str | None] = mapped_column(Text, nullable=True)

    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    computer: Mapped["Computer"] = relationship(back_populates="storage_devices")
