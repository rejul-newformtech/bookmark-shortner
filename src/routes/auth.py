from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.user import Token, UserCreate
from src.service.user import UserService

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post("/register")
async def register_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user_service = UserService(db)
    result = await user_service.create_user(user)
    return {
        "message": "User registered successfully",
        "user": result,
    }


# login endpoint
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    token = await user_service.login_user(form_data.username, form_data.password)
    return token

    """ TODO: Check credentials are valid , 2. Generate JWT token 3. send the token back to the user """
