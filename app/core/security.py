from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
oauth2_scheme = HTTPBearer()


def get_secret_key() -> str:
    return settings.SECRET_KEY


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(secret=password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(secret=plain_password, hash=hashed_password)


def create_access_token(data: dict[str, str], expires_delta: timedelta | None = None):
    to_encode: dict[str, Any] = data.copy()
    expire = datetime.now(tz=UTC) + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(claims=to_encode, key=get_secret_key(), algorithm=ALGORITHM)


def verify_access_token(token: str) -> str:
    payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
    username = payload.get("sub")
    if not isinstance(username, str):
        raise JWTError("Token subject is missing")
    return username
