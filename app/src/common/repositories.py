from config.db import async_session, Base
from sqlalchemy.future import select


class BaseRepository:
    def __init__(self, model_class: Base) -> None:
        self._model_class = model_class
        self._session_factory = async_session

    async def filter(self, **kwargs) -> list[Base]:
        async with self._session_factory() as session:
            async with session.begin():
                st = await session.execute(
                    select(self._model_class).filter_by(**kwargs)
                )

                return st.scalars().all()
