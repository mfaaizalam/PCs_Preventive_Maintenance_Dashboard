from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import UserRole
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.audit_log import AuditLog
   


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    role: Mapped[UserRole] = mapped_column(
        String(20),
        default=UserRole.VIEWER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    acknowledged_alerts: Mapped[list["Alert"]] = relationship(
        back_populates="acknowledged_by",
        foreign_keys="Alert.acknowledged_by_id",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
        passive_deletes=True,
    )
