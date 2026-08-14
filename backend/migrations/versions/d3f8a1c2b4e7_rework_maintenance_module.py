"""rework maintenance module: drop maintenance_assets, link maintenance_log to computers

Revision ID: d3f8a1c2b4e7
Revises: ab9b0f400992
Create Date: 2026-08-14 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d3f8a1c2b4e7"
down_revision: Union[str, Sequence[str], None] = "ab9b0f400992"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- computers: add S.No for the maintenance master list ---
    op.add_column("computers", sa.Column("s_no", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_computers_s_no"), "computers", ["s_no"], unique=True)

    # --- maintenance_tasks: add default responsible person ---
    op.add_column(
        "maintenance_tasks",
        sa.Column("responsible_person", sa.String(length=200), nullable=True),
    )

    # --- drop the old maintenance_log (pointed at maintenance_assets) ---
    op.drop_index(op.f("ix_maintenance_log_maintenance_task_id"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_maintenance_asset_id"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_id"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_completed_at"), table_name="maintenance_log")
    op.drop_table("maintenance_log")

    # --- drop maintenance_assets (specs now come from computers/agent) ---
    op.drop_index(op.f("ix_maintenance_assets_pc_no"), table_name="maintenance_assets")
    op.drop_index(op.f("ix_maintenance_assets_lab_section"), table_name="maintenance_assets")
    op.drop_index(op.f("ix_maintenance_assets_id"), table_name="maintenance_assets")
    op.drop_index(op.f("ix_maintenance_assets_asset_id"), table_name="maintenance_assets")
    op.drop_table("maintenance_assets")

    # --- recreate maintenance_log, now pointed at computers ---
    op.create_table(
        "maintenance_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("maintenance_task_id", sa.Integer(), nullable=False),
        sa.Column("period_label", sa.String(length=50), nullable=False),
        sa.Column("completed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("completed_by", sa.String(length=200), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["maintenance_task_id"], ["maintenance_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "computer_id", "maintenance_task_id", "period_label",
            name="uq_maintenance_log_computer_task_period",
        ),
    )
    op.create_index(op.f("ix_maintenance_log_id"), "maintenance_log", ["id"], unique=False)
    op.create_index(op.f("ix_maintenance_log_computer_id"), "maintenance_log", ["computer_id"], unique=False)
    op.create_index(op.f("ix_maintenance_log_maintenance_task_id"), "maintenance_log", ["maintenance_task_id"], unique=False)
    op.create_index(op.f("ix_maintenance_log_period_label"), "maintenance_log", ["period_label"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_maintenance_log_period_label"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_maintenance_task_id"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_computer_id"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_id"), table_name="maintenance_log")
    op.drop_table("maintenance_log")

    op.create_table(
        "maintenance_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pc_no", sa.String(length=50), nullable=False),
        sa.Column("lab_section", sa.String(length=100), nullable=False),
        sa.Column("specification", sa.Text(), nullable=True),
        sa.Column("asset_id", sa.String(length=50), nullable=True),
        sa.Column("default_owner", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_maintenance_assets_asset_id"), "maintenance_assets", ["asset_id"], unique=False)
    op.create_index(op.f("ix_maintenance_assets_id"), "maintenance_assets", ["id"], unique=False)
    op.create_index(op.f("ix_maintenance_assets_lab_section"), "maintenance_assets", ["lab_section"], unique=False)
    op.create_index(op.f("ix_maintenance_assets_pc_no"), "maintenance_assets", ["pc_no"], unique=True)

    op.create_table(
        "maintenance_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("maintenance_asset_id", sa.Integer(), nullable=False),
        sa.Column("maintenance_task_id", sa.Integer(), nullable=False),
        sa.Column("period_label", sa.String(length=50), nullable=False),
        sa.Column("responsible_person", sa.String(length=200), nullable=True),
        sa.Column("completed_by_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["completed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["maintenance_asset_id"], ["maintenance_assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["maintenance_task_id"], ["maintenance_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_maintenance_log_completed_at"), "maintenance_log", ["completed_at"], unique=False)
    op.create_index(op.f("ix_maintenance_log_id"), "maintenance_log", ["id"], unique=False)
    op.create_index(op.f("ix_maintenance_log_maintenance_asset_id"), "maintenance_log", ["maintenance_asset_id"], unique=False)
    op.create_index(op.f("ix_maintenance_log_maintenance_task_id"), "maintenance_log", ["maintenance_task_id"], unique=False)

    op.drop_column("maintenance_tasks", "responsible_person")

    op.drop_index(op.f("ix_computers_s_no"), table_name="computers")
    op.drop_column("computers", "s_no")