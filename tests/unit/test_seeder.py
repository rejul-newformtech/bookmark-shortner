import importlib.util
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import select

from app.models.bookmarks import Bookmark
from app.models.users import User
from app.models.visits import Visit

# Path to the seeder migration file
SEEDS_DIR = Path(__file__).resolve().parents[2] / "alembic" / "versions" / "seeders"
MIGRATION_FILE = SEEDS_DIR / "0001_seed_initial_data.py"

# Dynamically import the seeder migration
spec = importlib.util.spec_from_file_location("seeder_migration", str(MIGRATION_FILE))
assert spec is not None and spec.loader is not None
seeder_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seeder_mod)


class TestAlembicSeederConfiguration:
    """Validate Alembic multi-configuration and seeder migration attributes."""

    def test_alembic_ini_contains_seeders_section(self):
        """Verify alembic.ini contains [seeders] with dedicated version locations and table."""
        cfg = Config("alembic.ini", ini_section="seeders")
        assert cfg.config_ini_section == "seeders"

        version_locations = cfg.get_section_option("seeders", "version_locations")
        assert version_locations is not None
        assert "alembic/versions/seeders" in version_locations.replace("\\", "/")

        version_table = cfg.get_section_option("seeders", "version_table")
        assert version_table == "alembic_seeder_version"

    def test_normal_alembic_history_is_isolated(self):
        """Ensure normal [alembic] configuration defaults are untouched and isolated."""
        cfg = Config("alembic.ini", ini_section="alembic")
        assert cfg.config_ini_section == "alembic"
        version_table = cfg.get_section_option(
            "alembic", "version_table", "alembic_version"
        )
        assert version_table == "alembic_version"

    def test_seeder_migration_is_independent_root(self):
        """Verify seeder migration has its own root history (down_revision is None)."""
        assert seeder_mod.revision == "seeder_0001_initial_data"
        assert seeder_mod.down_revision is None


class TestAlembicSeederExecution:
    """Test seeder upgrade/downgrade execution and idempotency."""

    @pytest.mark.asyncio
    async def test_seeder_upgrade_and_downgrade(self, db_session, db_engine):
        """Verify upgrade seeds data safely and downgrade cleanly rolls back."""
        # Ensure clean state for seeded records
        await db_session.execute(
            seeder_mod.visit_table.delete().where(
                seeder_mod.visit_table.c.id.in_(
                    [
                        seeder_mod.SEED_VISIT_1_ID,
                        seeder_mod.SEED_VISIT_2_ID,
                        seeder_mod.SEED_VISIT_3_ID,
                        seeder_mod.SEED_VISIT_4_ID,
                        seeder_mod.SEED_VISIT_5_ID,
                    ]
                )
            )
        )
        await db_session.execute(
            seeder_mod.bookmark_table.delete().where(
                seeder_mod.bookmark_table.c.id.in_(
                    [
                        seeder_mod.SEED_BOOKMARK_1_ID,
                        seeder_mod.SEED_BOOKMARK_2_ID,
                        seeder_mod.SEED_BOOKMARK_3_ID,
                    ]
                )
            )
        )
        await db_session.execute(
            seeder_mod.user_table.delete().where(
                seeder_mod.user_table.c.id.in_(
                    [
                        seeder_mod.SEED_USER_1_ID,
                        seeder_mod.SEED_USER_2_ID,
                    ]
                )
            )
        )
        await db_session.commit()

        def run_upgrade(sync_conn):
            from alembic.runtime.migration import MigrationContext

            from alembic import op

            ctx = MigrationContext.configure(sync_conn)
            with op.Operations.context(ctx):
                seeder_mod.upgrade()

        async with db_engine.begin() as conn:
            await conn.run_sync(run_upgrade)

        # Verify seeded users exist
        user1 = await db_session.scalar(
            select(User).where(User.id == seeder_mod.SEED_USER_1_ID)
        )
        assert user1 is not None
        assert user1.username == "seed_demo_user"

        # Verify seeded bookmarks exist
        bm1 = await db_session.scalar(
            select(Bookmark).where(Bookmark.id == seeder_mod.SEED_BOOKMARK_1_ID)
        )
        assert bm1 is not None
        assert bm1.short_code == "seed_fast"
        assert bm1.user_id == seeder_mod.SEED_USER_1_ID

        # Verify visits exist
        visits = (
            await db_session.scalars(
                select(Visit).where(Visit.bookmark_id == seeder_mod.SEED_BOOKMARK_1_ID)
            )
        ).all()
        assert len(visits) == 3

        # Test idempotency - running upgrade again should succeed without duplicating or erroring
        async with db_engine.begin() as conn:
            await conn.run_sync(run_upgrade)

        visits_after = (
            await db_session.scalars(
                select(Visit).where(Visit.bookmark_id == seeder_mod.SEED_BOOKMARK_1_ID)
            )
        ).all()
        assert len(visits_after) == 3

        # Test downgrade - removes all seeded records
        def run_downgrade(sync_conn):
            from alembic.runtime.migration import MigrationContext

            from alembic import op

            ctx = MigrationContext.configure(sync_conn)
            with op.Operations.context(ctx):
                seeder_mod.downgrade()

        async with db_engine.begin() as conn:
            await conn.run_sync(run_downgrade)

        # Verify records are removed
        user_after = await db_session.scalar(
            select(User).where(User.id == seeder_mod.SEED_USER_1_ID)
        )
        assert user_after is None

        bm_after = await db_session.scalar(
            select(Bookmark).where(Bookmark.id == seeder_mod.SEED_BOOKMARK_1_ID)
        )
        assert bm_after is None
