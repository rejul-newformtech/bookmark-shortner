from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.visits import Visit


class Bookmark(Base):
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    short_code: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, nullable=False
    )
    visit_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id"))

    __table_args__ = (
        # Add a unique constraint on the combination of original_url and user_id
        UniqueConstraint("original_url", "user_id", name="uix_original_url_user_id"),
        Index("ix_bookmarks_original_url", original_url),
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="bookmarks",
    )
    visits: Mapped[list[Visit]] = relationship(
        back_populates="bookmark",
        cascade="all, delete-orphan",
    )
