"""add agent monitoring pause/resume fields

Revision ID: e4b1f6a9c210
Revises: 7a1c9e3f2b10
Create Date: 2026-09-27 00:00:00.000000

Adds:
  - computers.monitoring_paused           - true once the agent has actually
                                             stopped and acked the pause
                                             (used for "no extra software
                                             running" audit windows).
  - computers.pending_pause               - IT Manager requested a stop;
                                             cleared the moment the agent
                                             confirms it exited.
  - computers.pending_resume              - IT Manager requested a restart;
                                             cleared the moment the agent
                                             confirms it is reporting again.
  - computers.agent_action_requested_by   - who triggered the last pause/
                                             resume request (audit trail).
  - computers.agent_action_requested_at   - when that happened.

This mirrors the existing pending_shutdown pattern: the server only ever
sets a flag, the agent decides what to do with it and always exits/starts
for real - nothing here hides a running process from the OS.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e4b1f6a9c210"
down_revision: Union[str, Sequence[str], None] = "7a1c9e3f2b10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "computers",
        sa.Column("monitoring_paused", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "computers",
        sa.Column("pending_pause", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "computers",
        sa.Column("pending_resume", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "computers",
        sa.Column("agent_action_requested_by", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "computers",
        sa.Column("agent_action_requested_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("computers", "agent_action_requested_at")
    op.drop_column("computers", "agent_action_requested_by")
    op.drop_column("computers", "pending_resume")
    op.drop_column("computers", "pending_pause")
    op.drop_column("computers", "monitoring_paused")