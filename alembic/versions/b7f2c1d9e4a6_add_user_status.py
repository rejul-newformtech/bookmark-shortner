"""add user status

Revision ID: b7f2c1d9e4a6
Revises: 3a686a0cd43d
Create Date: 2026-08-28

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "b7f2c1d9e4a6"
down_revision: str | Sequence[str] | None = "3a686a0cd43d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


user_status = postgresql.ENUM("active", "inactive", "suspended", name="user_status")


def upgrade() -> None:
    user_status.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column(
            "status",
            user_status,
            server_default=sa.text("'active'"),
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE users SET status = CASE "
        "WHEN is_active THEN 'active'::user_status "
        "ELSE 'inactive'::user_status END"
    )
    op.alter_column("users", "status", nullable=False, server_default=None)
    op.drop_column("users", "is_active")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=True
        ),
    )
    op.execute(
        "UPDATE users SET is_active = CASE "
        "WHEN status = 'active'::user_status THEN true ELSE false END"
    )
    op.alter_column("users", "is_active", nullable=False, server_default=None)
    op.drop_column("users", "status")
    user_status.drop(op.get_bind(), checkfirst=True)
