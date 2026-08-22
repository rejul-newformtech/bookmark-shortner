from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.service.user import UserService
from src.database import get_db
from src.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    result = await user_service.create_user(user)
    return {"User registered successfully": result}
