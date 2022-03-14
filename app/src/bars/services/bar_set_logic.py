from bars.models import BarSet, Timeframe
from instruments.models import Instrument
from config.db import DB
from . import bar_set_crud


async def get_bar_set(db: DB, instrument: Instrument, timeframe: Timeframe) -> BarSet:
    return await bar_set_crud.get_or_create_bar_set(db, instrument, timeframe)
