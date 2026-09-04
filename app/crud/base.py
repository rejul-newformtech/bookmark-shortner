"""Common asynchronous CRUD functionality for database services."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel, default=Any)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel, default=Any)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD object with default methods to Create, Read, Update, Delete (CRUD).

    **Parameters**
    * `model`: A SQLAlchemy model class
    """

    model: type[ModelType]

    def __init__(self, model: type[ModelType] | None = None) -> None:
        if model is not None:
            self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        result = await db.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, object_id: Any) -> ModelType | None:
        return await self.get(db, object_id)

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_all(self, db: AsyncSession) -> list[ModelType]:
        result = await db.execute(select(self.model))
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType | dict[str, Any] | None = None,
        **values: Any,
    ) -> ModelType:
        if obj_in is not None:
            if isinstance(obj_in, dict):
                create_data = dict(obj_in)
            else:
                create_data = obj_in.model_dump(exclude_unset=True)
            create_data.update(values)
        else:
            create_data = values

        instance = self.model(**create_data)  # type: ignore[call-arg]
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType | None = None,
        object_id: Any = None,
        obj_in: UpdateSchemaType | dict[str, Any] | None = None,
        **values: Any,
    ) -> ModelType | None:
        instance = db_obj or (await self.get(db, object_id) if object_id else None)
        if instance is None:
            return None

        update_data: dict[str, Any] = {}
        if obj_in is not None:
            if isinstance(obj_in, dict):
                update_data = dict(obj_in)
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
        update_data.update(values)

        for field, value in update_data.items():
            setattr(instance, field, value)

        await db.commit()
        await db.refresh(instance)
        return instance

    async def delete(self, db: AsyncSession, object_id: Any) -> bool:
        result = await db.execute(
            delete(self.model).where(self.model.id == object_id)  # type: ignore[attr-defined]
        )
        await db.commit()
        rowcount = getattr(result, "rowcount", 0) or 0
        return bool(rowcount)

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
