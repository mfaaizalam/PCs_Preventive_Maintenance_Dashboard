from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.computer import Computer


class InstalledSoftware(Base, TimestampMixin):
    __tablename__ = "installed_software"
    __table_args__ = (
        UniqueConstraint(
            "computer_id",
            "name",
            "publisher",
            name="uq_installed_software_computer_name_publisher",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    computer_id: Mapped[int] = mapped_column(
        ForeignKey("computers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)

    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)

    version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    install_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_authorized: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    computer: Mapped["Computer"] = relationship(back_populates="installed_software")
