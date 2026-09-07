from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.visits import visit
from app.models.users import User
from app.schemas.bookmark import BookmarkResponse
from app.schemas.visits import (
    BookmarkVisitsResponse,
    Visited,
    VisitResponse,
)

router = APIRouter(
    prefix="/visited",
    tags=["visited"],
)


@router.post("/", response_model=VisitResponse)
async def create_visit(
    visited: Visited,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VisitResponse:
    result = await visit.visit(db, visited)
    return VisitResponse.model_validate(result)


@router.get("/", response_model=list[VisitResponse])
async def get_visits(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    bookmark_id: Annotated[UUID | None, None] = None,
) -> list[VisitResponse]:
    if bookmark_id is not None:
        bm = await visit.get_site_by_bookmark_id(
            db, bookmark_id=bookmark_id, user_id=current_user.id
        )
        if bm is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found",
            )
        result = await visit.get_by_bookmark_id(db, bookmark_id=bookmark_id)
        return [VisitResponse.model_validate(item) for item in result]

    result = await visit.get_all(db)
    return [VisitResponse.model_validate(item) for item in result]


@router.get("/bookmark/{bookmark_id}", response_model=BookmarkVisitsResponse)
@router.get(
    "/site/{bookmark_id}",
    response_model=BookmarkVisitsResponse,
    include_in_schema=False,
)
async def get_bookmark_site_visits(
    bookmark_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BookmarkVisitsResponse:
    """Fetch bookmark details and its visits using bookmark ID."""
    bm = await visit.get_site_by_bookmark_id(
        db, bookmark_id=bookmark_id, user_id=current_user.id
    )
    if bm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )

    visits_list = await visit.get_by_bookmark_id(db, bookmark_id=bookmark_id)
    return BookmarkVisitsResponse(
        bookmark=BookmarkResponse.model_validate(bm),
        visits=[VisitResponse.model_validate(v) for v in visits_list],
    )


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VisitResponse:
    result = await visit.get_by_id(db, visit_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found"
        )
    return VisitResponse.model_validate(result)


@router.put("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: UUID,
    visited: Visited,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VisitResponse:
    result = await visit.update(db, object_id=visit_id, bookmark_id=visited.bookmark_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found"
        )
    return VisitResponse.model_validate(result)


@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visit(
    visit_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    deleted = await visit.delete(db, visit_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found"
        )
