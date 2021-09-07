from instruments.models import Instrument
from bars.models import BarLot, Bar, Range, Timeframe
from asyncpg.exceptions import UniqueViolationError
from . import range_crud
from loguru import logger


async def create_bars(bar_lot: BarLot, bars: list[Bar]) -> None:
    if bars:
        try:
            await Bar.objects.bulk_create(bars)
        except UniqueViolationError:
            pass

        # TODO: This is ok?
        # min_ts = min(bars, key=lambda bar: bar.t).t
        # max_ts = max(bars, key=lambda bar: bar.t).t
        # range = Range(from_t=min_ts, to_t=max_ts)
        # await range_crud.create_range(instrument, timeframe, range)

        # logger.debug(f'Bars created. Instrument: {instrument}. Range: {range}')


async def get_bars(bar_lot: BarLot, range: Range) -> list[Bar]:
    return await Bar.objects.filter(
        bar_lot=bar_lot, t__gte=range.from_t, t__lte=range.to_t
    ).all()
