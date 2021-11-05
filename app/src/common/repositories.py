from typing import Type, TypeVar, Generic
from config.db import async_session
from common.models import Model
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

T = TypeVar('T', bound=Model)


class BaseRepository(Generic[T]):
    NoResultError = NoResultFound

    def __init__(self, model: Type[T]) -> None:
        self._model = model
        self._session_factory = async_session

    async def create(self, *joins, **kwargs) -> T:
        async with self._session_factory() as session:
            async with session.begin():
                instance = self._model(**kwargs)
                session.add(instance)
                await session.commit()

                instance = await self.get(*joins, id=instance.id)

                return instance

    async def get(self, *joins, **kwargs) -> T:
        async with self._session_factory() as session:
            async with session.begin():
                query = select(self._model).filter_by(**kwargs)

                if joins:
                    query = query.options(joinedload(*joins))

                result = await session.execute(query)

                return result.scalar_one()

    async def get_or_create(self, *joins, **kwargs) -> tuple[T, bool]:
        async with self._session_factory() as session:
            async with session.begin():
                try:
                    instance = await self.get(*joins, **kwargs)
                    is_created = False

                except self.NoResultError:
                    instance = await self.create(*joins, **kwargs)
                    is_created = True

            return instance, is_created

    async def update(self, instance: T, **kwargs) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)

                values = kwargs or instance.dict(exclude_none=True)

                await session.execute(
                    update(self._model)
                    .where(self._model.id == instance.id)
                    .values(values)
                )

    async def filter(self, **kwargs) -> list[T]:
        async with self._session_factory() as session:
            async with session.begin():
                result = await session.execute(select(self._model).filter_by(**kwargs))

                return result.scalars().all()

    async def delete(self, instance: T) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                await session.delete(instance)
