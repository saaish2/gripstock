"""inspections, damage reports, maintenance orders

Revision ID: 0006_operations
Revises: 0005_billing
Create Date: 2024-01-15
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006_operations"
down_revision = "0005_billing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inspections",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("reservation_id", sa.Integer, sa.ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("phase", sa.String(12), nullable=False),
        sa.Column("condition", sa.String(20), nullable=False),
        sa.Column("inspector_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "damage_reports",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reservation_id", sa.Integer, sa.ForeignKey("reservations.id", ondelete="SET NULL")),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("estimated_repair_cost", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("billable", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("resolved", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("reported_by_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "maintenance_orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("summary", sa.String(255), nullable=False),
        sa.Column("details", sa.Text),
        sa.Column("labor_cost", sa.Numeric(12, 2), server_default="0"),
        sa.Column("parts_cost", sa.Numeric(12, 2), server_default="0"),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_maintenance_orders_status", "maintenance_orders", ["status"])


def downgrade() -> None:
    op.drop_table("maintenance_orders")
    op.drop_table("damage_reports")
    op.drop_table("inspections")
