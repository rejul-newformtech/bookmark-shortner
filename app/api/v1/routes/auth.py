from typing import Annotated

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.logger import get_logger
from app.crud.user import user
from app.schemas.user import Token, UserCreate, UserResponse

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


async def login_form(
    username: Annotated[str, Form()], password: Annotated[str, Form()]
):
    """Parse the username and password submitted through the login form."""
    return {"username": username, "password": password}


@router.post("/register")
async def register_user(
    user_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user."""
    logger.info("Register attempt for username=%s", user_in.username)
    result = await user.create_user(db, user_in)
    logger.info("User registered successfully: %s", result.username)
    return {
        "message": "User registered successfully",
        "user": UserResponse.model_validate(result),
    }


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[dict, Depends(login_form)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate a user and return an access token."""
    username = form_data["username"]
    logger.info("Login attempt for username=%s", username)
    token = await user.login_user(db, username, form_data["password"])
    logger.info("Successful login for username=%s", username)
    return token
