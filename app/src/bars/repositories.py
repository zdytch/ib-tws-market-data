from common.repositories import BaseRepository
from common.schemas import Range
from .models import Bar, BarSet, BarRange
from sqlalchemy.future import select


class BarRepository(BaseRepository):
    async def get_bars_in_range(self, bar_set: BarSet, range: Range) -> list[Bar]:
        async with self._session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(Bar)
                    .where(Bar.bar_set == bar_set)
                    .where(Bar.timestamp >= range.from_dt)
                    .where(Bar.timestamp <= range.to_dt)
                )

            return result.scalars().all()


bar_repo = BarRepository(Bar)
bar_set_repo = BaseRepository(BarSet)
bar_range_repo = BaseRepository(BarRange)
