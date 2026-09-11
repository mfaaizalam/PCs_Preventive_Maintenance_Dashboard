"""add remote shutdown fields to computers

Revision ID: 7a1c9e3f2b10
Revises: f3a7c8e1b502
Create Date: 2026-09-10
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "7a1c9e3f2b10"
down_revision: Union[str, Sequence[str], None] = "f3a7c8e1b502"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "computers",
        sa.Column("pending_shutdown", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "computers",
        sa.Column("shutdown_requested_by", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "computers",
        sa.Column("shutdown_requested_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("computers", "shutdown_requested_at")
    op.drop_column("computers", "shutdown_requested_by")
    op.drop_column("computers", "pending_shutdown")