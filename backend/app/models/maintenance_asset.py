from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.maintenance_log import MaintenanceLog


class MaintenanceAsset(Base, TimestampMixin):
    __tablename__ = "maintenance_assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    pc_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    lab_section: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    specification: Mapped[str | None] = mapped_column(Text, nullable=True)

    asset_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Cross-reference to computers.asset_id when agent is enrolled",
    )

    default_owner: Mapped[str | None] = mapped_column(String(200), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(
        back_populates="maintenance_asset",
        cascade="all, delete-orphan",
    )
