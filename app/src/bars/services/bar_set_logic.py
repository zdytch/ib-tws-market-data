from bars.models import BarSet, Timeframe
from instruments.models import Instrument
from sqlalchemy.ext.asyncio import AsyncSession
from . import bar_set_crud


async def get_bar_set(
    session: AsyncSession, instrument: Instrument, timeframe: Timeframe
) -> BarSet:
    return await bar_set_crud.get_or_create_bar_set(session, instrument, timeframe)
