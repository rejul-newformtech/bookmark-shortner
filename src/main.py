from fastapi import FastAPI

app = FastAPI(
    title="Link Shortener API",
    version="1.0.0",
    description="This is a simple API for shortening URLs.",
)


@app.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "healthy"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
