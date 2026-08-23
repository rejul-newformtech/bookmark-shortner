from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.schemas.bookmark import BookmarkCreate, BookmarkResponse
from src.service.bookmark import BookmarkService
from src.utils.auth import get_current_user
from src.utils.shortner import create_unique_short_code

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"],
)


@router.post("/", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark: BookmarkCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):

    short_code = await create_unique_short_code(db)
    bookmark_service = BookmarkService(db)
    result = await bookmark_service.db_bookmark(
        user_id=current_user.id, url=str(bookmark.original_url), short_code=short_code
    )
    return result


@router.get("/", response_model=list[BookmarkResponse])
async def get_bookmarks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    bookmark_service = BookmarkService(db)
    result = await bookmark_service.get_bookmarks(user_id=current_user.id)
    return result


@router.get("/{short_code}", response_model=BookmarkResponse)
async def get_bookmark_by_short_code(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    short_code: str,
):
    bookmark_service = BookmarkService(db)
    result = await bookmark_service.get_bookmark_by_short_code(
        short_code=short_code, user_id=current_user.id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    return result
