from indicators.models import Indicator
from bars.models import BarSet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound


async def get_or_create_indicator(
    session: AsyncSession, bar_set: BarSet, length: int
) -> Indicator:
    try:
        query = select(Indicator).filter_by(bar_set=bar_set, length=length)
        indicator = (await session.execute(query)).scalar_one()

    except NoResultFound:
        indicator = Indicator(bar_set_id=bar_set.id, length=length)
        session.add(indicator)

        await session.commit()

    return indicator
