from typing import Optional
from common.repositories import BaseRepository
from common.schemas import Range
from .models import Bar, BarSet, BarRange
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime


class BarRepository(BaseRepository):
    async def bulk_save(self, bars: list[Bar]) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                values = [bar.db_values() for bar in bars]
                query = insert(Bar).values(values).on_conflict_do_nothing()

                await session.execute(query)

    async def get_bars_in_range(self, bar_set: BarSet, range: Range) -> list[Bar]:
        async with self._session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(Bar)
                    .where(Bar.bar_set == bar_set)
                    .where(Bar.timestamp >= range.from_dt)
                    .where(Bar.timestamp <= range.to_dt)
                    .order_by(Bar.timestamp)
                )

            return result.scalars().all()

    async def get_latest_timestamp(self, bar_set: BarSet) -> Optional[datetime]:
        async with self._session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(func.max(Bar.timestamp)).filter_by(bar_set=bar_set)
                )

                return result.scalar()


bar_repo = BarRepository(Bar)
bar_set_repo = BaseRepository(BarSet)
bar_range_repo = BaseRepository(BarRange)
