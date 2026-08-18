from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import ComputerStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.hardware_change_log import HardwareChangeLog
    from app.models.installed_software import InstalledSoftware
    from app.models.maintenance_log import MaintenanceLog
    from app.models.peripheral import Peripheral
    from app.models.peripheral_event import PeripheralEvent
    from app.models.ram_slot import RamSlot
    from app.models.software_license import SoftwareLicense
    from app.models.storage_device import StorageDevice


class Computer(Base, TimestampMixin):
    __tablename__ = "computers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    agent_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    asset_id: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )

    hardware_uuid: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )

    hostname: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    # Serial number for the maintenance master list (S.No column in
    # the Excel). Nullable + admin-assigned - agents never set this,
    # it's purely for matching the department's existing paper/Excel
    # numbering, assigned once when a PC is added to the checklist.
    s_no: Mapped[int | None] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
        index=True,
    )

    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    lab_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    lab_section: Mapped[str | None] = mapped_column(String(100), nullable=True)

    os_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    os_version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    cpu_model: Mapped[str | None] = mapped_column(String(200), nullable=True)

    cpu_usage_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    cpu_temperature_celsius: Mapped[float | None] = mapped_column(Float, nullable=True)

    ram_total_gb: Mapped[float | None] = mapped_column(Float, nullable=True)

    ram_usage_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    disk_total_gb: Mapped[float | None] = mapped_column(Float, nullable=True)

    disk_usage_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    uptime_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[ComputerStatus] = mapped_column(
        String(20),
        default=ComputerStatus.UNKNOWN,
        nullable=False,
    )

    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ram_slots: Mapped[list["RamSlot"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )
    storage_devices: Mapped[list["StorageDevice"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )
    peripherals: Mapped[list["Peripheral"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )
    peripheral_events: Mapped[list["PeripheralEvent"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )
    software_licenses: Mapped[list["SoftwareLicense"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )
    installed_software: Mapped[list["InstalledSoftware"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )
    hardware_change_logs: Mapped[list["HardwareChangeLog"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )
    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(
        back_populates="computer",
        cascade="all, delete-orphan",
    )