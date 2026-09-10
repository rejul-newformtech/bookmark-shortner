"""use singular table names

Revision ID: c4d8e2f1a907
Revises: b7f2c1d9e4a6
Create Date: 2026-08-29

"""

from collections.abc import Sequence

from alembic import op


revision: str = "c4d8e2f1a907"
down_revision: str | Sequence[str] | None = "b7f2c1d9e4a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("users", "user")
    op.rename_table("bookmarks", "bookmark")
    op.rename_table("visits", "visit")


def downgrade() -> None:
    op.rename_table("visit", "visits")
    op.rename_table("bookmark", "bookmarks")
    op.rename_table("user", "users")
