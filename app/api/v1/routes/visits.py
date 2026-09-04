from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.visits import visit
from app.models.users import User
from app.schemas.visits import Visited, VisitResponse

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
) -> list[VisitResponse]:
    result = await visit.get_all(db)
    return [VisitResponse.model_validate(item) for item in result]


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
