from bars.models import BarSet, Timeframe
from instruments.models import Instrument
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound


async def get_or_create_bar_set(
    session: AsyncSession, instrument: Instrument, timeframe: Timeframe
) -> BarSet:
    try:
        query = (
            select(BarSet)
            .filter_by(instrument=instrument, timeframe=timeframe)
            .options(joinedload('instrument'))
        )
        bar_set = (await session.execute(query)).scalar_one()

    except NoResultFound:
        bar_set = BarSet(
            instrument_id=instrument.id, instrument=instrument, timeframe=timeframe
        )
        session.add(bar_set)

        await session.commit()

    return bar_set
