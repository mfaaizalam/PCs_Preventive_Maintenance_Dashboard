"""extend computers table and create full lab monitoring schema

Revision ID: b7c4e2a91d03
Revises: 193fd880cb36
Create Date: 2026-08-08 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c4e2a91d03"
down_revision: Union[str, Sequence[str], None] = "193fd880cb36"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("computers", sa.Column("asset_id", sa.String(length=50), nullable=True))
    op.add_column("computers", sa.Column("hardware_uuid", sa.String(length=100), nullable=True))
    op.add_column("computers", sa.Column("lab_section", sa.String(length=100), nullable=True))
    op.add_column("computers", sa.Column("os_name", sa.String(length=100), nullable=True))
    op.add_column("computers", sa.Column("os_version", sa.String(length=100), nullable=True))
    op.add_column("computers", sa.Column("cpu_model", sa.String(length=200), nullable=True))
    op.add_column("computers", sa.Column("cpu_usage_percent", sa.Float(), nullable=True))
    op.add_column("computers", sa.Column("cpu_temperature_celsius", sa.Float(), nullable=True))
    op.add_column("computers", sa.Column("ram_total_gb", sa.Float(), nullable=True))
    op.add_column("computers", sa.Column("ram_usage_percent", sa.Float(), nullable=True))
    op.add_column("computers", sa.Column("disk_total_gb", sa.Float(), nullable=True))
    op.add_column("computers", sa.Column("disk_usage_percent", sa.Float(), nullable=True))
    op.add_column("computers", sa.Column("uptime_seconds", sa.Integer(), nullable=True))
    op.add_column(
        "computers",
        sa.Column("status", sa.String(length=20), server_default="unknown", nullable=False),
    )
    op.add_column(
        "computers",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    with op.batch_alter_table("computers") as batch_op:
        batch_op.alter_column("created_at", type_=sa.DateTime(timezone=True))
        batch_op.alter_column("last_seen", type_=sa.DateTime(timezone=True))

    op.create_index(op.f("ix_computers_asset_id"), "computers", ["asset_id"], unique=True)
    op.create_index(
        op.f("ix_computers_hardware_uuid"),
        "computers",
        ["hardware_uuid"],
        unique=True,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=True),
        sa.Column("role", sa.String(length=20), server_default="viewer", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "maintenance_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pc_no", sa.String(length=50), nullable=False),
        sa.Column("lab_section", sa.String(length=100), nullable=False),
        sa.Column("specification", sa.Text(), nullable=True),
        sa.Column("asset_id", sa.String(length=50), nullable=True),
        sa.Column("default_owner", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_maintenance_assets_asset_id"), "maintenance_assets", ["asset_id"], unique=False)
    op.create_index(op.f("ix_maintenance_assets_id"), "maintenance_assets", ["id"], unique=False)
    op.create_index(op.f("ix_maintenance_assets_lab_section"), "maintenance_assets", ["lab_section"], unique=False)
    op.create_index(op.f("ix_maintenance_assets_pc_no"), "maintenance_assets", ["pc_no"], unique=True)

    op.create_table(
        "maintenance_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "default_frequency",
            sa.String(length=20),
            server_default="biweekly",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_maintenance_tasks_id"), "maintenance_tasks", ["id"], unique=False)

    op.create_table(
        "ram_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("slot_number", sa.Integer(), nullable=False),
        sa.Column("capacity_gb", sa.Float(), nullable=True),
        sa.Column("manufacturer", sa.String(length=100), nullable=True),
        sa.Column("speed_mhz", sa.Integer(), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("computer_id", "slot_number", name="uq_ram_slots_computer_slot"),
    )
    op.create_index(op.f("ix_ram_slots_computer_id"), "ram_slots", ["computer_id"], unique=False)
    op.create_index(op.f("ix_ram_slots_id"), "ram_slots", ["id"], unique=False)

    op.create_table(
        "storage_devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("device_identifier", sa.String(length=200), nullable=False),
        sa.Column("device_type", sa.String(length=20), server_default="other", nullable=False),
        sa.Column("model", sa.String(length=200), nullable=True),
        sa.Column("capacity_gb", sa.Float(), nullable=True),
        sa.Column("health_status", sa.String(length=20), server_default="unknown", nullable=False),
        sa.Column("smart_status", sa.Text(), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "computer_id",
            "device_identifier",
            name="uq_storage_devices_computer_device",
        ),
    )
    op.create_index(op.f("ix_storage_devices_computer_id"), "storage_devices", ["computer_id"], unique=False)
    op.create_index(op.f("ix_storage_devices_id"), "storage_devices", ["id"], unique=False)

    op.create_table(
        "peripherals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("device_key", sa.String(length=255), nullable=False),
        sa.Column("device_type", sa.String(length=30), nullable=False),
        sa.Column("vendor_id", sa.String(length=20), nullable=True),
        sa.Column("product_id", sa.String(length=20), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("port_path", sa.String(length=255), nullable=True),
        sa.Column("friendly_name", sa.String(length=200), nullable=True),
        sa.Column("model", sa.String(length=200), nullable=True),
        sa.Column("capacity_gb", sa.Float(), nullable=True),
        sa.Column("volume_label", sa.String(length=100), nullable=True),
        sa.Column("descriptor", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="disconnected", nullable=False),
        sa.Column("is_expected", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("computer_id", "device_key", name="uq_peripherals_computer_device_key"),
    )
    op.create_index(op.f("ix_peripherals_computer_id"), "peripherals", ["computer_id"], unique=False)
    op.create_index(op.f("ix_peripherals_id"), "peripherals", ["id"], unique=False)

    op.create_table(
        "software_licenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("vendor", sa.String(length=200), nullable=True),
        sa.Column("version", sa.String(length=100), nullable=True),
        sa.Column("license_type", sa.String(length=20), server_default="unknown", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="unknown", nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("renewal_contact", sa.String(length=200), nullable=True),
        sa.Column("alert_schedule_days", sa.String(length=50), nullable=True),
        sa.Column("is_activated", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("detected_automatically", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "computer_id",
            "product_name",
            name="uq_software_licenses_computer_product",
        ),
    )
    op.create_index(op.f("ix_software_licenses_computer_id"), "software_licenses", ["computer_id"], unique=False)
    op.create_index(op.f("ix_software_licenses_id"), "software_licenses", ["id"], unique=False)

    op.create_table(
        "installed_software",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("publisher", sa.String(length=200), nullable=True),
        sa.Column("version", sa.String(length=100), nullable=True),
        sa.Column("install_date", sa.Date(), nullable=True),
        sa.Column("is_authorized", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "computer_id",
            "name",
            "publisher",
            name="uq_installed_software_computer_name_publisher",
        ),
    )
    op.create_index(op.f("ix_installed_software_computer_id"), "installed_software", ["computer_id"], unique=False)
    op.create_index(op.f("ix_installed_software_id"), "installed_software", ["id"], unique=False)

    op.create_table(
        "metrics_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("cpu_usage_percent", sa.Float(), nullable=True),
        sa.Column("ram_usage_percent", sa.Float(), nullable=True),
        sa.Column("disk_usage_percent", sa.Float(), nullable=True),
        sa.Column("cpu_temperature_celsius", sa.Float(), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
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

    op.create_table(
        "hardware_change_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=20), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_identifier", sa.String(length=255), nullable=True),
        sa.Column("field_name", sa.String(length=100), nullable=True),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hardware_change_log_changed_at"), "hardware_change_log", ["changed_at"], unique=False)
    op.create_index(op.f("ix_hardware_change_log_computer_id"), "hardware_change_log", ["computer_id"], unique=False)
    op.create_index(op.f("ix_hardware_change_log_id"), "hardware_change_log", ["id"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=True),
        sa.Column("alert_type", sa.String(length=20), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("is_acknowledged", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("acknowledged_by_id", sa.Integer(), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["acknowledged_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_computer_id"), "alerts", ["computer_id"], unique=False)
    op.create_index(op.f("ix_alerts_created_at"), "alerts", ["created_at"], unique=False)
    op.create_index(op.f("ix_alerts_id"), "alerts", ["id"], unique=False)

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_log_created_at"), "audit_log", ["created_at"], unique=False)
    op.create_index(op.f("ix_audit_log_id"), "audit_log", ["id"], unique=False)
    op.create_index(op.f("ix_audit_log_user_id"), "audit_log", ["user_id"], unique=False)

    op.create_table(
        "maintenance_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("maintenance_asset_id", sa.Integer(), nullable=False),
        sa.Column("maintenance_task_id", sa.Integer(), nullable=False),
        sa.Column("period_label", sa.String(length=50), nullable=False),
        sa.Column("responsible_person", sa.String(length=200), nullable=True),
        sa.Column("completed_by_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["completed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["maintenance_asset_id"], ["maintenance_assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["maintenance_task_id"], ["maintenance_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_maintenance_log_completed_at"), "maintenance_log", ["completed_at"], unique=False)
    op.create_index(op.f("ix_maintenance_log_id"), "maintenance_log", ["id"], unique=False)
    op.create_index(op.f("ix_maintenance_log_maintenance_asset_id"), "maintenance_log", ["maintenance_asset_id"], unique=False)
    op.create_index(op.f("ix_maintenance_log_maintenance_task_id"), "maintenance_log", ["maintenance_task_id"], unique=False)

    op.create_table(
        "peripheral_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computer_id", sa.Integer(), nullable=False),
        sa.Column("peripheral_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=20), nullable=False),
        sa.Column("device_type", sa.String(length=30), nullable=True),
        sa.Column("device_key", sa.String(length=255), nullable=True),
        sa.Column("vendor_id", sa.String(length=20), nullable=True),
        sa.Column("product_id", sa.String(length=20), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("port_path", sa.String(length=255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["peripheral_id"], ["peripherals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_peripheral_events_computer_id"), "peripheral_events", ["computer_id"], unique=False)
    op.create_index(op.f("ix_peripheral_events_id"), "peripheral_events", ["id"], unique=False)
    op.create_index(op.f("ix_peripheral_events_occurred_at"), "peripheral_events", ["occurred_at"], unique=False)
    op.create_index(op.f("ix_peripheral_events_peripheral_id"), "peripheral_events", ["peripheral_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_peripheral_events_peripheral_id"), table_name="peripheral_events")
    op.drop_index(op.f("ix_peripheral_events_occurred_at"), table_name="peripheral_events")
    op.drop_index(op.f("ix_peripheral_events_id"), table_name="peripheral_events")
    op.drop_index(op.f("ix_peripheral_events_computer_id"), table_name="peripheral_events")
    op.drop_table("peripheral_events")

    op.drop_index(op.f("ix_maintenance_log_maintenance_task_id"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_maintenance_asset_id"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_id"), table_name="maintenance_log")
    op.drop_index(op.f("ix_maintenance_log_completed_at"), table_name="maintenance_log")
    op.drop_table("maintenance_log")

    op.drop_index(op.f("ix_audit_log_user_id"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_id"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_created_at"), table_name="audit_log")
    op.drop_table("audit_log")

    op.drop_index(op.f("ix_alerts_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_created_at"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_computer_id"), table_name="alerts")
    op.drop_table("alerts")

    op.drop_index(op.f("ix_hardware_change_log_id"), table_name="hardware_change_log")
    op.drop_index(op.f("ix_hardware_change_log_computer_id"), table_name="hardware_change_log")
    op.drop_index(op.f("ix_hardware_change_log_changed_at"), table_name="hardware_change_log")
    op.drop_table("hardware_change_log")

    op.drop_index("ix_metrics_history_computer_recorded_at", table_name="metrics_history")
    op.drop_index(op.f("ix_metrics_history_id"), table_name="metrics_history")
    op.drop_index(op.f("ix_metrics_history_computer_id"), table_name="metrics_history")
    op.drop_table("metrics_history")

    op.drop_index(op.f("ix_installed_software_id"), table_name="installed_software")
    op.drop_index(op.f("ix_installed_software_computer_id"), table_name="installed_software")
    op.drop_table("installed_software")

    op.drop_index(op.f("ix_software_licenses_id"), table_name="software_licenses")
    op.drop_index(op.f("ix_software_licenses_computer_id"), table_name="software_licenses")
    op.drop_table("software_licenses")

    op.drop_index(op.f("ix_peripherals_id"), table_name="peripherals")
    op.drop_index(op.f("ix_peripherals_computer_id"), table_name="peripherals")
    op.drop_table("peripherals")

    op.drop_index(op.f("ix_storage_devices_id"), table_name="storage_devices")
    op.drop_index(op.f("ix_storage_devices_computer_id"), table_name="storage_devices")
    op.drop_table("storage_devices")

    op.drop_index(op.f("ix_ram_slots_id"), table_name="ram_slots")
    op.drop_index(op.f("ix_ram_slots_computer_id"), table_name="ram_slots")
    op.drop_table("ram_slots")

    op.drop_index(op.f("ix_maintenance_tasks_id"), table_name="maintenance_tasks")
    op.drop_table("maintenance_tasks")

    op.drop_index(op.f("ix_maintenance_assets_pc_no"), table_name="maintenance_assets")
    op.drop_index(op.f("ix_maintenance_assets_lab_section"), table_name="maintenance_assets")
    op.drop_index(op.f("ix_maintenance_assets_id"), table_name="maintenance_assets")
    op.drop_index(op.f("ix_maintenance_assets_asset_id"), table_name="maintenance_assets")
    op.drop_table("maintenance_assets")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_computers_hardware_uuid"), table_name="computers")
    op.drop_index(op.f("ix_computers_asset_id"), table_name="computers")
    op.drop_column("computers", "updated_at")
    op.drop_column("computers", "status")
    op.drop_column("computers", "uptime_seconds")
    op.drop_column("computers", "disk_usage_percent")
    op.drop_column("computers", "disk_total_gb")
    op.drop_column("computers", "ram_usage_percent")
    op.drop_column("computers", "ram_total_gb")
    op.drop_column("computers", "cpu_temperature_celsius")
    op.drop_column("computers", "cpu_usage_percent")
    op.drop_column("computers", "cpu_model")
    op.drop_column("computers", "os_version")
    op.drop_column("computers", "os_name")
    op.drop_column("computers", "lab_section")
    op.drop_column("computers", "hardware_uuid")
    op.drop_column("computers", "asset_id")

    with op.batch_alter_table("computers") as batch_op:
        batch_op.alter_column("created_at", type_=sa.DateTime())
        batch_op.alter_column("last_seen", type_=sa.DateTime())
