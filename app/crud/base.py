"""Common asynchronous CRUD functionality for database services."""

from typing import TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class CRUDBase[ModelType]:
    """Provide common database operations for model-specific services."""

    model: type[ModelType]

    async def create(self, db: AsyncSession, **values: object) -> ModelType:
        instance = self.model(**values)  # type: ignore[call-arg]
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def get_by_id(self, db: AsyncSession, object_id: object) -> ModelType | None:
        result = await db.execute(
            select(self.model).where(self.model.id == object_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession) -> list[ModelType]:
        result = await db.execute(select(self.model))
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, object_id: object, **values: object
    ) -> ModelType | None:
        instance = await self.get_by_id(db, object_id)
        if instance is None:
            return None
        for field, value in values.items():
            setattr(instance, field, value)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def delete(self, db: AsyncSession, object_id: object) -> bool:
        result = await db.execute(
            delete(self.model).where(self.model.id == object_id)  # type: ignore[attr-defined]
        )
        await db.commit()
        rowcount = getattr(result, "rowcount", 0) or 0
        return bool(rowcount)
