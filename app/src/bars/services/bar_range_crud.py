from bars.models import BarSet, BarRange
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_bar_ranges(session: AsyncSession, bar_set: BarSet) -> list[BarRange]:
    result = await session.execute(select(BarRange).filter_by(bar_set=bar_set))

    return result.scalars().all()
