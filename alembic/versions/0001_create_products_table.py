"""create products table

Revision ID: 0001_create_products_table
Revises:
Create Date: 2026-06-22 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_products_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.execute("CREATE INDEX ix_products_updated_at_id_desc ON products (updated_at DESC, id DESC)")
    op.execute("CREATE INDEX ix_products_category_updated_at_id_desc ON products (category, updated_at DESC, id DESC)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_products_category_updated_at_id_desc")
    op.execute("DROP INDEX IF EXISTS ix_products_updated_at_id_desc")
    op.drop_table("products")
