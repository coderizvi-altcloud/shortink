"""initial shortlink schema

Revision ID: 0001_initial_shortlink
Revises: 
Create Date: 2026-07-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial_shortlink"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shortlink",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("short_code", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("click_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.UniqueConstraint("url"),
        sa.UniqueConstraint("short_code"),
    )
    op.create_index(op.f("ix_shortlink_id"), "shortlink", ["id"], unique=False)
    op.create_index(op.f("ix_shortlink_url"), "shortlink", ["url"], unique=True)
    op.create_index(op.f("ix_shortlink_short_code"), "shortlink", ["short_code"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_shortlink_short_code"), table_name="shortlink")
    op.drop_index(op.f("ix_shortlink_url"), table_name="shortlink")
    op.drop_index(op.f("ix_shortlink_id"), table_name="shortlink")
    op.drop_table("shortlink")
