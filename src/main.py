from fastapi import FastAPI

from src.routes.auth import router as auth_router
from src.routes.bookmarks import router as bookmarks_router

app = FastAPI(
    title="Link Shortener API",
    version="1.0.0",
    description="This is a simple API for shortening URLs.",
)

app.include_router(auth_router)
app.include_router(bookmarks_router)


@app.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "healthy"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
