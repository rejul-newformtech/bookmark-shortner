from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logger import get_logger
from app.core.security import create_access_token, get_hashed_password
from app.crud.base import CRUDBase
from app.models.bookmarks import Bookmark
from app.models.users import User
from app.schemas.user import Token, UserCreate
from app.utils.auth import authenticate_user

logger = get_logger(__name__)


class UserService(CRUDBase[User]):
    model = User

    async def get_user_profile_by_username(
        self,
        db: AsyncSession,
        username: str,
    ) -> User:
        logger.info("Fetching user profile for username=%s", username)
        result = await db.execute(
            select(User)
            .options(selectinload(User.bookmarks).selectinload(Bookmark.visits))
            .where(User.username == username)
        )

        db_user = result.unique().scalar_one_or_none()

        if db_user is None:
            logger.warning("User profile not found for username=%s", username)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return db_user

    async def create_user(self, db: AsyncSession, user_create: UserCreate) -> User:
        logger.info("Attempting to create user username=%s", user_create.username)
        result = await db.execute(
            select(User).where(User.username == user_create.username)
        )
        existing_user_by_username = result.scalars().first()
        if existing_user_by_username:
            logger.warning(
                "Registration failed: duplicate username=%s", user_create.username
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        result = await db.execute(select(User).where(User.email == user_create.email))
        existing_user_by_email = result.scalars().first()
        if existing_user_by_email:
            logger.warning("Registration failed: duplicate email=%s", user_create.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
        hashed_password = get_hashed_password(user_create.password)

        user = await self.create(
            db,
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
        )
        logger.info("User created successfully username=%s", user.username)
        return user

    async def login_user(self, db: AsyncSession, username: str, password: str) -> Token:
        logger.info("Login attempt username=%s", username)
        user = await authenticate_user(db, username, password)
        if not user:
            logger.warning("Failed login attempt username=%s", username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        access_token_expires = timedelta(minutes=10)

        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        logger.info("Login success username=%s", username)

        return Token(access_token=access_token, token_type="bearer")


user_service = UserService()
