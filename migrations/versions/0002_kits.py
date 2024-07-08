"""kits and kit items

Revision ID: 0002_kits
Revises: 0001_baseline
Create Date: 2023-03-02
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_kits"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "kits",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("description", sa.Text),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("bundle_discount_rate", sa.Numeric(5, 4), nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "kit_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("kit_id", sa.Integer, sa.ForeignKey("kits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.UniqueConstraint("kit_id", "asset_id", name="uq_kit_asset"),
    )


def downgrade() -> None:
    op.drop_table("kit_items")
    op.drop_table("kits")
