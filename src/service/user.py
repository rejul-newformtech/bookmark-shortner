from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.utils.auth import get_hashed_password
from src.models.user import User
from src.schemas.user import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_create: UserCreate) -> User:
        # Check if the username already exists
        result = await self.db.execute(
            select(User).where(User.username == user_create.username)
        )
        existing_user_by_username = result.scalars().first()
        if existing_user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        # Check if the email already exists
        result = await self.db.execute(
            select(User).where(User.email == user_create.email)
        )
        existing_user_by_email = result.scalars().first()
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
        hashed_password = get_hashed_password(user_create.password)

        new_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
