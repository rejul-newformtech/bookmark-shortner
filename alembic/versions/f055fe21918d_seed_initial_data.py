"""seed initial data

Revision ID: f055fe21918d
Revises: 37352d51d4d5
Create Date: 2026-09-04
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from passlib.context import CryptContext

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f055fe21918d"
down_revision: str | Sequence[str] | None = "37352d51d4d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Deterministic IDs so seeds are reproducible
SEED_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
SEED_BOOKMARK_1 = uuid.UUID("00000000-0000-0000-0000-000000000011")
SEED_BOOKMARK_2 = uuid.UUID("00000000-0000-0000-0000-000000000012")

# Define lightweight table representations for data operations
user_status_enum = sa.Enum(
    "active",
    "inactive",
    "suspended",
    name="user_status",
).with_variant(
    sa.dialects.postgresql.ENUM(
        "active", "inactive", "suspended", name="user_status", create_type=False
    ),
    "postgresql",
)

user_table = sa.table(
    "user",
    sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
    sa.column("username", sa.String),
    sa.column("email", sa.String),
    sa.column("hashed_password", sa.String),
    sa.column("status", user_status_enum),
    sa.column("created_at", sa.DateTime(timezone=True)),
)

bookmark_table = sa.table(
    "bookmark",
    sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
    sa.column("original_url", sa.String),
    sa.column("short_code", sa.String),
    sa.column("visit_count", sa.Integer),
    sa.column("user_id", sa.dialects.postgresql.UUID(as_uuid=True)),
    sa.column("created_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    now = datetime.now(UTC)
    hashed_pwd = pwd_context.hash("AdminPass123!@#")

    # 1. Seed initial admin user
    op.bulk_insert(
        user_table,
        [
            {
                "id": SEED_USER_ID,
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": hashed_pwd,
                "status": "active",
                "created_at": now,
            }
        ],
    )

    # 2. Seed initial bookmarks linked to that user
    op.bulk_insert(
        bookmark_table,
        [
            {
                "id": SEED_BOOKMARK_1,
                "original_url": "https://fastapi.tiangolo.com",
                "short_code": "fastapi",
                "visit_count": 0,
                "user_id": SEED_USER_ID,
                "created_at": now,
            },
            {
                "id": SEED_BOOKMARK_2,
                "original_url": "https://python.org",
                "short_code": "python",
                "visit_count": 0,
                "user_id": SEED_USER_ID,
                "created_at": now,
            },
        ],
    )


def downgrade() -> None:
    # Remove seeded bookmarks first (foreign key constraint)
    op.execute(
        bookmark_table.delete().where(
            bookmark_table.c.id.in_([SEED_BOOKMARK_1, SEED_BOOKMARK_2])
        )
    )
    # Remove seeded user
    op.execute(user_table.delete().where(user_table.c.id == SEED_USER_ID))
