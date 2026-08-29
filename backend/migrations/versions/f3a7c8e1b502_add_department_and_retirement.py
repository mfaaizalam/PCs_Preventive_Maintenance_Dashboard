"""add department field and computer auto-retirement columns

Revision ID: f3a7c8e1b502
Revises: 12bebe94db90
Create Date: 2026-08-29 00:00:00.000000

Adds:
  - computers.department   - free-text dept tag, admin-editable only
                              (agents never send this), defaults to "IMD"
                              for every existing + future row.
  - computers.is_retired    - true once the offline-sweep decides a PC
                              is a dead/replaced seat rather than just
                              temporarily offline (see
                              computer_service.auto_retire_stale_computers).
                              Never deletes the row - just hides it from
                              the default dashboard/export views.
  - computers.retired_at    - when that happened, for display/debugging.

Both is_retired/retired_at are cleared automatically the moment the same
computer row reports in again (see ingest_agent_report), so a PC that
comes back from being "retired" needs zero manual admin action either way.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3a7c8e1b502"
down_revision: Union[str, Sequence[str], None] = "12bebe94db90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "computers",
        sa.Column("department", sa.String(length=100), server_default="IMD", nullable=True),
    )
    op.add_column(
        "computers",
        sa.Column("is_retired", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "computers",
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_computers_is_retired"), "computers", ["is_retired"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_computers_is_retired"), table_name="computers")
    op.drop_column("computers", "retired_at")
    op.drop_column("computers", "is_retired")
    op.drop_column("computers", "department")