from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.bookmarks import router as bookmarks_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.visits import router as visits_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(bookmarks_router)
api_router.include_router(users_router)
api_router.include_router(visits_router)
