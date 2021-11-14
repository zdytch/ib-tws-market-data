from bars.models import BarSet, BarInterval
from config.db import DB
from sqlalchemy.future import select


async def get_bar_intervals(db: DB, bar_set: BarSet) -> list[BarInterval]:
    result = await db.execute(select(BarInterval).filter_by(bar_set=bar_set))

    return result.scalars().all()
