from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.bookmark import bookmark
from app.models.users import User
from app.schemas.bookmark import (
    BookmarkBatchUploadResponse,
    BookmarkCreate,
    BookmarkResponse,
    BookmarkSortBy,
    SortOrder,
)
from app.service.analytics import record_visit_background
from app.service.pdf_extractor import extract_urls_from_pdf
from app.utils.shortner import create_unique_short_code

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"],
)

# Base , need crud in singleton


@router.post("/upload-pdf", response_model=BookmarkBatchUploadResponse)
async def upload_bookmarks_pdf(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Upload a PDF file containing URLs, extract them concurrently using a dedicated
    thread pool, generate shortcodes for new URLs, reuse existing shortcodes for
    already bookmarked URLs, and return all bookmarks with a status message.
    """
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a PDF",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    try:
        urls = await extract_urls_from_pdf(content)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    if not urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No URLs found in the uploaded PDF",
        )

    (
        bookmarks_list,
        created_count,
        existing_count,
    ) = await bookmark.batch_process_pdf_urls(
        db=db,
        user_id=current_user.id,
        urls=urls,
    )

    message = (
        "Some of them already exist"
        if existing_count > 0
        else "All bookmarks created successfully"
    )

    return BookmarkBatchUploadResponse(
        message=message,
        total_found=len(urls),
        created_count=created_count,
        existing_count=existing_count,
        bookmarks=[BookmarkResponse.model_validate(b) for b in bookmarks_list],
    )


@router.post("/", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark_in: BookmarkCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    short_code = await create_unique_short_code(db)
    result = await bookmark.db_bookmark(
        db=db,
        user_id=current_user.id,
        url=str(bookmark_in.original_url),
        short_code=short_code,
    )
    return result


@router.get("/", response_model=list[BookmarkResponse])
async def get_bookmarks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[
        str | None, Query(description="Search bookmarks by URL or short code")
    ] = None,
    sort_by: Annotated[
        BookmarkSortBy,
        Query(
            description="Field to sort by: created_at, visit_count, original_url, short_code",
        ),
    ] = BookmarkSortBy.CREATED_AT,
    order: Annotated[
        SortOrder,
        Query(
            description="Sort direction: asc or desc (default: desc)",
        ),
    ] = SortOrder.DESC,
):
    result = await bookmark.get_bookmarks(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by.value,
        order=order.value,
    )
    return result


@router.get("/{short_code}", response_model=BookmarkResponse)
async def get_bookmark_by_short_code(
    short_code: str,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    This endpoint is used to retrieve a bookmark by its short code.
    It also records a visit to the bookmark in the database and increments
    the visit count.
    """
    result = await bookmark.get_bookmark_by_short_code(
        db=db, short_code=short_code, user_id=current_user.id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    # Added Background task for recodring visit and analytics
    background_tasks.add_task(record_visit_background, bookmark_id=result.id)
    return result
