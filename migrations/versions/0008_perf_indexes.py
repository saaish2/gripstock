"""performance indexes for hot query paths

Revision ID: 0008_perf_indexes
Revises: 0007_platform
Create Date: 2024-11-22
"""
from __future__ import annotations

from alembic import op

revision = "0008_perf_indexes"
down_revision = "0007_platform"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_assets_barcode", "assets", ["barcode"])
    op.create_index("ix_assets_serial_number", "assets", ["serial_number"])
    op.create_index("ix_reservations_customer_id", "reservations", ["customer_id"])
    op.create_index("ix_rental_orders_customer_id", "rental_orders", ["customer_id"])
    op.create_index("ix_invoices_customer_id", "invoices", ["customer_id"])
    op.create_index("ix_payments_invoice_id", "payments", ["invoice_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", "audit_logs")
    op.drop_index("ix_payments_invoice_id", "payments")
    op.drop_index("ix_invoices_customer_id", "invoices")
    op.drop_index("ix_rental_orders_customer_id", "rental_orders")
    op.drop_index("ix_reservations_customer_id", "reservations")
    op.drop_index("ix_assets_serial_number", "assets")
    op.drop_index("ix_assets_barcode", "assets")
