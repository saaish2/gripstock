"""reservations and reservation lines

Revision ID: 0003_reservations
Revises: 0002_kits
Create Date: 2023-05-11
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_reservations"
down_revision = "0002_kits"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("reference", sa.String(20), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_by_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("picked_up_at", sa.DateTime(timezone=True)),
        sa.Column("returned_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reservations_status", "reservations", ["status"])
    op.create_index("ix_reservations_starts_at", "reservations", ["starts_at"])
    op.create_index("ix_reservations_ends_at", "reservations", ["ends_at"])

    op.create_table(
        "reservation_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("reservation_id", sa.Integer, sa.ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("kit_id", sa.Integer, sa.ForeignKey("kits.id", ondelete="SET NULL")),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
    )
    op.create_index("ix_reservation_lines_asset_id", "reservation_lines", ["asset_id"])


def downgrade() -> None:
    op.drop_table("reservation_lines")
    op.drop_table("reservations")
