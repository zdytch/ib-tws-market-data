from bars.models import BarSet, Timeframe
from instruments.models import Instrument
from config.db import DB
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound


async def get_or_create_bar_set(
    db: DB, instrument: Instrument, timeframe: Timeframe
) -> BarSet:
    try:
        query = (
            select(BarSet)
            .filter_by(instrument=instrument, timeframe=timeframe)
            .options(joinedload('instrument'))
        )
        bar_set = (await db.execute(query)).scalar_one()

    except NoResultFound:
        bar_set = BarSet(
            instrument_id=instrument.id, instrument=instrument, timeframe=timeframe
        )
        db.add(bar_set)

        await db.commit()

    return bar_set
