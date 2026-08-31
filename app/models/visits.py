from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.bookmarks import Bookmark


class Visit(Base):
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    bookmark_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookmark.id"),
        nullable=False,
    )

    visited_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    bookmark: Mapped[Bookmark] = relationship(back_populates="visits")
