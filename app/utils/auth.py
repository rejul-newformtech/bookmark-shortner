from sqlalchemy import select

from app.core.security import verify_password


async def authenticate_user(db, username: str, password: str):
    from app.models.users import User

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
