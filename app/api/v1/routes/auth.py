from typing import Annotated

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.user import user_service
from app.schemas.user import Token, UserCreate

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


async def login_form(username: Annotated[str, Form], password: Annotated[str, Form]):
    """Parse the username and password submitted through the login form."""
    return {"username": username, "password": password}


@router.post("/register")
async def register_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """Register a new user."""
    result = await user_service.create_user(db, user)
    return {
        "message": "User registered successfully",
        "user": result,
    }


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[dict, Depends(login_form)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate a user and return an access token."""
    token = await user_service.login_user(
        db, form_data["username"], form_data["password"]
    )
    return token
