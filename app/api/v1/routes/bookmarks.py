from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.bookmark import bookmark_service
from app.models.users import User
from app.schemas.bookmark import BookmarkCreate, BookmarkResponse
from app.utils.shortner import create_unique_short_code

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"],
)

# Base , need crud in singleton


@router.post("/", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark: BookmarkCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):

    short_code = await create_unique_short_code(db)
    result = await bookmark_service.db_bookmark(
        db=db,
        user_id=current_user.id,
        url=str(bookmark.original_url),
        short_code=short_code,
    )
    return result


@router.get("/", response_model=list[BookmarkResponse])
async def get_bookmarks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await bookmark_service.get_bookmarks(db=db, user_id=current_user.id)
    return result


@router.get("/{short_code}", response_model=BookmarkResponse)
async def get_bookmark_by_short_code(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    short_code: str,
):
    result = await bookmark_service.get_bookmark_by_short_code(
        db=db, short_code=short_code, user_id=current_user.id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    return result
