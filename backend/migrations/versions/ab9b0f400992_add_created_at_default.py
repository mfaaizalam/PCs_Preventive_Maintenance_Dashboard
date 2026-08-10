from alembic import op
import sqlalchemy as sa


revision = "ab9b0f400992"
down_revision = "b7c4e2a91d03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "computers",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )


def downgrade() -> None:
    op.alter_column(
        "computers",
        "created_at",
        server_default=None,
    )