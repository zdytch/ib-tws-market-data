from typing import Type
from config.db import async_session
from common.models import BaseModel
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError


class BaseRepository:
    NoResultError = NoResultFound
    DuplicateError = IntegrityError

    def __init__(self, model_class: Type[BaseModel]) -> None:
        self._model_class = model_class
        self._session_factory = async_session

    async def create(self, *joins, **kwargs) -> Type[BaseModel]:
        async with self._session_factory() as session:
            async with session.begin():
                instance = self._model_class(**kwargs)
                session.add(instance)
                await session.commit()

                instance = await self.get(*joins, id=instance.id)

                return instance

    async def get(self, *joins: str, **kwargs) -> Type[BaseModel]:
        async with self._session_factory() as session:
            async with session.begin():
                query = select(self._model_class).filter_by(**kwargs)

                if joins:
                    query = query.options(joinedload(*joins))

                result = await session.execute(query)

                return result.scalar_one()

    async def get_or_create(self, *joins, **kwargs) -> tuple[Type[BaseModel], bool]:
        async with self._session_factory() as session:
            async with session.begin():
                try:
                    instance = await self.get(*joins, **kwargs)
                    is_created = False

                except self.NoResultError:
                    instance = await self.create(*joins, **kwargs)
                    is_created = True

            return instance, is_created

    async def update(self, instance: BaseModel, **kwargs) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)

                values = kwargs or instance.db_values()

                await session.execute(
                    update(self._model_class)
                    .where(self._model_class.id == instance.id)
                    .values(values)
                )

    async def filter(self, **kwargs) -> list[Type[BaseModel]]:
        async with self._session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(self._model_class).filter_by(**kwargs)
                )

                return result.scalars().all()

    async def delete(self, instance: BaseModel) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                await session.delete(instance)
