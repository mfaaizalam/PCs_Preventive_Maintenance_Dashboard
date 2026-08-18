"""drop metrics_history table

Revision ID: 12bebe94db90
Revises: d3f8a1c2b4e7
Create Date: 2026-08-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "12bebe94db90"
down_revision: Union[str, Sequence[str], None] = "d3f8a1c2b4e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Metric History was a separate rolling-window table (CPU/RAM/Disk
    per check-in) with no working frontend chart on top of it. Removed
    entirely per Module 2 - the live values already shown on PC cards
    are the CPU/RAM/Disk snapshot columns on `computers`, which stay.
    """
    op.drop_index("ix_metrics_history_computer_recorded_at", table_name="metrics_history")
    op.drop_index(op.f("ix_metrics_history_id"), table_name="metrics_history")
    op.drop_index(op.f("ix_metrics_history_computer_id"), table_name="metrics_history")
    op.drop_table("metrics_history")


def downgrade() -> None:
    op.create_table(
        "metrics_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("cpu_usage_percent", sa.Float(), nullable=True),
        sa.Column("ram_usage_percent", sa.Float(), nullable=True),
        sa.Column("disk_usage_percent", sa.Float(), nullable=True),
        sa.Column("cpu_temperature_celsius", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_metrics_history_computer_id"), "metrics_history", ["computer_id"], unique=False)
    op.create_index(op.f("ix_metrics_history_id"), "metrics_history", ["id"], unique=False)
    op.create_index(
        "ix_metrics_history_computer_recorded_at",
        "metrics_history",
        ["computer_id", "recorded_at"],
        unique=False,
    )