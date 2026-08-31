# src/db/base.py

import re
from typing import cast

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr


def snake_case(name: str) -> str:
    """Convert a class name from CamelCase to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class CustomBase:
    """Provide convention-based table names for SQLAlchemy models."""

    @declared_attr  # type: ignore[arg-type]
    def __tablename__(cls) -> str:
        class_name = cast(type[object], cls).__name__
        return snake_case(class_name)


# Keep constraint names consistent across migrations and database environments.
meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base(CustomBase, DeclarativeBase):
    """Base class inherited by all database models."""

    metadata = meta
