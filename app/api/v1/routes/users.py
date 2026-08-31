from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.user import user_service
from app.schemas.user import UserProfileResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}/profile", response_model=UserProfileResponse)
async def get_user_profile_by_username(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await user_service.get_user_profile_by_username(db, username)
