"""create orders table

Revision ID: 20260327_0001
Revises: 
Create Date: 2026-03-27

"""

from alembic import op
import sqlalchemy as sa


revision = "20260327_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    order_status = sa.Enum(
        "pending",
        "processing",
        "done",
        "failed",
        name="order_status",
    )
    order_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "status",
            order_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_orders_id", "orders", ["id"])
    op.create_index("ix_orders_user_id", "orders", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_index("ix_orders_id", table_name="orders")
    op.drop_table("orders")

    order_status = sa.Enum(
        "pending",
        "processing",
        "done",
        "failed",
        name="order_status",
    )
    order_status.drop(op.get_bind(), checkfirst=True)

