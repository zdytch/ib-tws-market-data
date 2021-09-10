from bars.models import BarSet, Bar, Range, Timeframe
from instruments.models import Instrument
from instruments import services as instrument_services
from . import crud
from ib.connector import ib_connector
from datetime import datetime
import pytz
from loguru import logger


async def get_bar_set(instrument: Instrument, timeframe: Timeframe) -> BarSet:
    return await BarSet.objects.select_related('instrument').get_or_create(
        instrument=instrument, timeframe=timeframe
    )


async def get_bars(bar_set: BarSet, range: Range) -> list[Bar]:
    existing_ranges = await Range.objects.filter(bar_set=bar_set).all()
    missing_ranges = _calculate_missing_ranges(range, existing_ranges)
    instrument = bar_set.instrument

    for missing_range in missing_ranges:
        # If missing range doesn't overlap with open session range
        if not await instrument_services.is_overlap_open_session(
            instrument, missing_range.from_t, missing_range.to_t
        ):
            # Extend missing range by 1 day to overlap possible gaps in db
            missing_range.from_t -= 86400
            missing_range.to_t += 86400

        logger.debug(
            f'Missing bars in range. Retreiving from origin... Instrument: {instrument}. Range: {missing_range}'
        )

        try:
            origin_bars = await _get_bars_from_origin(
                instrument, bar_set.timeframe, missing_range
            )
            await crud.add_bars(bar_set, origin_bars)

            logger.debug(f'Bars created. Instrument: {instrument}. Range: {range}')
        except Exception as e:
            logger.debug(e)

    bars = await crud.get_bars(bar_set, range)

    return bars


async def get_latest_timestamp(bar_set: BarSet) -> int:
    return await Bar.objects.filter(bar_set=bar_set).max('t') or 0


async def _get_bars_from_origin(
    instrument: Instrument, timeframe: Timeframe, range: Range
) -> list[Bar]:
    from_dt = datetime.fromtimestamp(range.from_t, pytz.utc)
    to_dt = datetime.fromtimestamp(range.to_t, pytz.utc)
    bars = await ib_connector.get_historical_bars(instrument, timeframe, from_dt, to_dt)

    if bars:
        logger.debug(
            f'Received bars from origin. Instrument: {instrument}. Range: {range}'
        )
    else:
        logger.debug(f'No bars from origin. Instrument: {instrument}. Range: {range}')

    return bars


def _calculate_missing_ranges(
    within_range: Range, existing_ranges: list[Range]
) -> list:
    missing_ranges = []
    next_from_t = within_range.from_t

    for range in existing_ranges:
        if range.to_t > within_range.from_t and range.from_t < within_range.to_t:
            if range.from_t > next_from_t < within_range.to_t:
                missing_ranges.append(Range(from_t=next_from_t, to_t=range.from_t))

            next_from_t = range.to_t

    if next_from_t < within_range.to_t:
        missing_ranges.append(Range(from_t=next_from_t, to_t=within_range.to_t))

    return missing_ranges
