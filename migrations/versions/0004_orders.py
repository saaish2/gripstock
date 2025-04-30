"""rental orders and order lines

Revision ID: 0004_orders
Revises: 0003_reservations
Create Date: 2023-07-20
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_orders"
down_revision = "0003_reservations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rental_orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("reference", sa.String(20), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reservation_id", sa.Integer, sa.ForeignKey("reservations.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), server_default="0"),
        sa.Column("discount_total", sa.Numeric(12, 2), server_default="0"),
        sa.Column("deposit_total", sa.Numeric(12, 2), server_default="0"),
        sa.Column("tax_total", sa.Numeric(12, 2), server_default="0"),
        sa.Column("grand_total", sa.Numeric(12, 2), server_default="0"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_rental_orders_status", "rental_orders", ["status"])

    op.create_table(
        "order_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("rental_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("rental_days", sa.Integer, nullable=False, server_default="1"),
        sa.Column("unit_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("line_subtotal", sa.Numeric(12, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("deposit_amount", sa.Numeric(12, 2), server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("order_lines")
    op.drop_table("rental_orders")
