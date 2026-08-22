from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column;
from uuid import UUID as PyUUID
import uuid

from src.db.base import Base
from src.models.user import User


class Bookmark(Base):
    __tablename__ = "bookmarks"
    """" Bookmark model """
    id : Mapped[PyUUID]= mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    short_code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    visit_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id:Mapped[PyUUID] = mapped_column(UUID(as_uuid=True),ForeignKey(User.id))

    __table_args__ = (
        # Add a unique constraint on the combination of original_url and user_id   
        UniqueConstraint('original_url', 'user_id', name='uix_original_url_user_id'),
        Index('ix_bookmarks_original_url', original_url)
    )