from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.users import UserStatus


class VisitSummary(BaseModel):
    id: UUID
    visited_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class BookmarkSummary(BaseModel):
    id: UUID
    original_url: str
    short_code: str
    visit_count: int
    created_at: datetime | None = None
    visits: list[VisitSummary] = []

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not any(character.islower() for character in password):
            raise ValueError("Password must contain a lowercase letter")
        if not any(character.isupper() for character in password):
            raise ValueError("Password must contain an uppercase letter")
        if not any(character.isdigit() for character in password):
            raise ValueError("Password must contain a digit")
        if not any(character in "@$!%*?&#" for character in password):
            raise ValueError("Password must contain a special character")
        return password


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    status: UserStatus | None = None


class UserResponse(UserBase):
    id: UUID
    status: UserStatus

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    email: str
    status: UserStatus
    created_at: datetime | None = None
    bookmarks: list[BookmarkSummary] = []

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
