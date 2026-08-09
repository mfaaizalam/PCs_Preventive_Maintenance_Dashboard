from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import LicenseStatus, LicenseType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.computer import Computer


class SoftwareLicense(Base, TimestampMixin):
    __tablename__ = "software_licenses"
    __table_args__ = (
        UniqueConstraint(
            "computer_id",
            "product_name",
            name="uq_software_licenses_computer_product",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_name: Mapped[str] = mapped_column(String(200), nullable=False)

    vendor: Mapped[str | None] = mapped_column(String(200), nullable=True)

    version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    license_type: Mapped[LicenseType] = mapped_column(
        String(20),
        default=LicenseType.UNKNOWN,
        nullable=False,
    )

    status: Mapped[LicenseStatus] = mapped_column(
        String(20),
        default=LicenseStatus.UNKNOWN,
        nullable=False,
    )

    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    renewal_contact: Mapped[str | None] = mapped_column(String(200), nullable=True)

    alert_schedule_days: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Comma-separated days before expiry to alert, e.g. 30,14,7,1",
    )

    is_activated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    detected_automatically: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    computer: Mapped["Computer"] = relationship(back_populates="software_licenses")
