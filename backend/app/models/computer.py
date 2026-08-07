from datetime import datetime

from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Computer(Base):
    __tablename__ = "computers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    agent_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    hostname: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True
    )

    lab_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    is_online: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )