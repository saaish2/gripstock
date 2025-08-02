"""invoices and payments

Revision ID: 0005_billing
Revises: 0004_orders
Create Date: 2023-09-28
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_billing"
down_revision = "0004_orders"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("number", sa.String(24), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("rental_orders.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("issued_on", sa.Date),
        sa.Column("due_on", sa.Date),
        sa.Column("subtotal", sa.Numeric(12, 2), server_default="0"),
        sa.Column("late_fee_total", sa.Numeric(12, 2), server_default="0"),
        sa.Column("damage_total", sa.Numeric(12, 2), server_default="0"),
        sa.Column("tax_total", sa.Numeric(12, 2), server_default="0"),
        sa.Column("total", sa.Numeric(12, 2), server_default="0"),
        sa.Column("amount_paid", sa.Numeric(12, 2), server_default="0"),
        sa.Column("voided_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_invoices_status", "invoices", ["status"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("invoice_id", sa.Integer, sa.ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("method", sa.String(20), nullable=False),
        sa.Column("reference", sa.String(120)),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_refund", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("invoices")
