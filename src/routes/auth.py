from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post("/register", response_model=None)
async def register_user(user: None, db: None):
    """TODO
    check if user already exists
    check if email already exists
    create new user
    send response with success message
    """
