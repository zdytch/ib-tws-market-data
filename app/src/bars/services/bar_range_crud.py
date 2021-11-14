from bars.models import BarSet, BarRange
from config.db import DB
from sqlalchemy.future import select


async def get_bar_ranges(db: DB, bar_set: BarSet) -> list[BarRange]:
    result = await db.execute(select(BarRange).filter_by(bar_set=bar_set))

    return result.scalars().all()
