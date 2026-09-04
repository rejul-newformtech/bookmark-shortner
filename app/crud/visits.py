from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.visits import Visit
from app.schemas.visits import VisitCreate, Visited, VisitUpdate


class CRUDVisit(CRUDBase[Visit, VisitCreate, VisitUpdate]):
    async def visit(self, db: AsyncSession, visited: Visited) -> Visit:
        return await self.create(db, bookmark_id=UUID(str(visited.bookmark_id)))


visit = CRUDVisit(Visit)
