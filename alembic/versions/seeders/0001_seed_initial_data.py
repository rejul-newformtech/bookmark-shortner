"""Seed initial application data for users, bookmarks, and visits.

Revision ID: seeder_0001_initial_data
Revises: None
Create Date: 2026-09-07
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from passlib.context import CryptContext
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "seeder_0001_initial_data"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Deterministic UUIDs for reproducibility and idempotent tracking
SEED_USER_1_ID = uuid.UUID("a0000000-0000-4000-8000-000000000001")
SEED_USER_2_ID = uuid.UUID("a0000000-0000-4000-8000-000000000002")

SEED_BOOKMARK_1_ID = uuid.UUID("b0000000-0000-4000-8000-000000000001")
SEED_BOOKMARK_2_ID = uuid.UUID("b0000000-0000-4000-8000-000000000002")
SEED_BOOKMARK_3_ID = uuid.UUID("b0000000-0000-4000-8000-000000000003")

SEED_VISIT_1_ID = uuid.UUID("c0000000-0000-4000-8000-000000000001")
SEED_VISIT_2_ID = uuid.UUID("c0000000-0000-4000-8000-000000000002")
SEED_VISIT_3_ID = uuid.UUID("c0000000-0000-4000-8000-000000000003")
SEED_VISIT_4_ID = uuid.UUID("c0000000-0000-4000-8000-000000000004")
SEED_VISIT_5_ID = uuid.UUID("c0000000-0000-4000-8000-000000000005")

# Dialect-safe user_status enum
user_status_enum = sa.Enum(
    "active",
    "inactive",
    "suspended",
    name="user_status",
).with_variant(
    postgresql.ENUM(
        "active", "inactive", "suspended", name="user_status", create_type=False
    ),
    "postgresql",
)

# Lightweight SQLAlchemy table representations matching production models
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

visit_table = sa.table(
    "visit",
    sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
    sa.column("bookmark_id", sa.dialects.postgresql.UUID(as_uuid=True)),
    sa.column("visited_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    """Seed initial records idempotently."""
    now = datetime.now(UTC)
    bind = op.get_bind()

    # 1. Seed Users
    seed_users = [
        {
            "id": SEED_USER_1_ID,
            "username": "seed_demo_user",
            "email": "demo_user@seed.example.com",
            "hashed_password": pwd_context.hash("DemoPass123!@#"),
            "status": "active",
            "created_at": now,
        },
        {
            "id": SEED_USER_2_ID,
            "username": "seed_dev_user",
            "email": "dev_user@seed.example.com",
            "hashed_password": pwd_context.hash("DevPass123!@#"),
            "status": "active",
            "created_at": now,
        },
    ]

    existing_users = bind.execute(
        sa.select(user_table.c.id, user_table.c.username, user_table.c.email).where(
            (user_table.c.id.in_([u["id"] for u in seed_users]))
            | (user_table.c.username.in_([u["username"] for u in seed_users]))
            | (user_table.c.email.in_([u["email"] for u in seed_users]))
        )
    ).fetchall()
    existing_user_ids = {row[0] for row in existing_users}
    existing_usernames = {row[1] for row in existing_users}
    existing_emails = {row[2] for row in existing_users}

    users_to_insert = [
        u
        for u in seed_users
        if u["id"] not in existing_user_ids
        and u["username"] not in existing_usernames
        and u["email"] not in existing_emails
    ]
    if users_to_insert:
        op.bulk_insert(user_table, users_to_insert)

    # 2. Seed Bookmarks (linked strictly to seeded users)
    seed_bookmarks = [
        {
            "id": SEED_BOOKMARK_1_ID,
            "user_id": SEED_USER_1_ID,
            "original_url": "https://fastapi.tiangolo.com/tutorial/",
            "short_code": "seed_fast",
            "visit_count": 3,
            "created_at": now,
        },
        {
            "id": SEED_BOOKMARK_2_ID,
            "user_id": SEED_USER_1_ID,
            "original_url": "https://docs.python.org/3/library/",
            "short_code": "seed_py",
            "visit_count": 2,
            "created_at": now,
        },
        {
            "id": SEED_BOOKMARK_3_ID,
            "user_id": SEED_USER_2_ID,
            "original_url": "https://www.sqlalchemy.org/features.html",
            "short_code": "seed_sqla",
            "visit_count": 1,
            "created_at": now,
        },
    ]

    existing_bms = bind.execute(
        sa.select(bookmark_table.c.id, bookmark_table.c.short_code).where(
            (bookmark_table.c.id.in_([b["id"] for b in seed_bookmarks]))
            | (
                bookmark_table.c.short_code.in_(
                    [b["short_code"] for b in seed_bookmarks]
                )
            )
        )
    ).fetchall()
    existing_bm_ids = {row[0] for row in existing_bms}
    existing_short_codes = {row[1] for row in existing_bms}

    bms_to_insert = [
        b
        for b in seed_bookmarks
        if b["id"] not in existing_bm_ids
        and b["short_code"] not in existing_short_codes
    ]
    if bms_to_insert:
        op.bulk_insert(bookmark_table, bms_to_insert)

    # 3. Seed Visits (linked to seeded bookmarks)
    seed_visits = [
        {
            "id": SEED_VISIT_1_ID,
            "bookmark_id": SEED_BOOKMARK_1_ID,
            "visited_at": now,
        },
        {
            "id": SEED_VISIT_2_ID,
            "bookmark_id": SEED_BOOKMARK_1_ID,
            "visited_at": now,
        },
        {
            "id": SEED_VISIT_3_ID,
            "bookmark_id": SEED_BOOKMARK_1_ID,
            "visited_at": now,
        },
        {
            "id": SEED_VISIT_4_ID,
            "bookmark_id": SEED_BOOKMARK_2_ID,
            "visited_at": now,
        },
        {
            "id": SEED_VISIT_5_ID,
            "bookmark_id": SEED_BOOKMARK_3_ID,
            "visited_at": now,
        },
    ]

    existing_visit_ids = set(
        bind.execute(
            sa.select(visit_table.c.id).where(
                visit_table.c.id.in_([v["id"] for v in seed_visits])
            )
        )
        .scalars()
        .all()
    )
    visits_to_insert = [v for v in seed_visits if v["id"] not in existing_visit_ids]
    if visits_to_insert:
        op.bulk_insert(visit_table, visits_to_insert)


def downgrade() -> None:
    """Remove seeded records in reverse dependency order."""
    all_visit_ids = [
        SEED_VISIT_1_ID,
        SEED_VISIT_2_ID,
        SEED_VISIT_3_ID,
        SEED_VISIT_4_ID,
        SEED_VISIT_5_ID,
    ]
    all_bookmark_ids = [
        SEED_BOOKMARK_1_ID,
        SEED_BOOKMARK_2_ID,
        SEED_BOOKMARK_3_ID,
    ]
    all_user_ids = [
        SEED_USER_1_ID,
        SEED_USER_2_ID,
    ]

    # Delete visits
    op.execute(visit_table.delete().where(visit_table.c.id.in_(all_visit_ids)))
    # Delete bookmarks
    op.execute(bookmark_table.delete().where(bookmark_table.c.id.in_(all_bookmark_ids)))
    # Delete users
    op.execute(user_table.delete().where(user_table.c.id.in_(all_user_ids)))
