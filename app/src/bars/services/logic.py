from bars.schemas import Bar, BarList, Timeframe, Range
from . import bar_crud, range_crud
from instruments.schemas import Instrument
from ib.connector import ib_connector
from datetime import datetime
import pytz
from loguru import logger


async def get_bar_list(
    instrument: Instrument, timeframe: Timeframe, from_t: int, to_t: int
) -> BarList:
    range = Range(from_t=from_t, to_t=to_t)

    cache_ranges = await range_crud.read_range_list(instrument, timeframe)
    missing_ranges = _calculate_missing_ranges(range, cache_ranges)

    for missing_range in missing_ranges:
        # If missing range doesn't overlap with open session range
        if not _is_overlap_open_session_range(instrument, missing_range):
            # Extend missing range by 1 day to overlap possible gaps in cache
            missing_range.from_t -= 86400
            missing_range.to_t += 86400

        logger.debug(
            f'Missing bars in cache. Retreiving from origin... Instrument: {instrument}. Range: {missing_range}'
        )

        try:
            origin_bars = await _get_bars_from_origin(
                instrument, timeframe, missing_range
            )
            await bar_crud.create_bars(instrument, timeframe, origin_bars)
        except Exception as e:
            logger.debug(e)

    bars = await bar_crud.read_bars(instrument, timeframe, range)

    return BarList(instrument=instrument, timeframe=timeframe, bars=bars)


async def get_last_timestamp(instrument: Instrument, timeframe: Timeframe) -> int:
    return await bar_crud.get_last_bar_timestamp(instrument, timeframe)


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


def _is_overlap_open_session_range(instrument: Instrument, range: Range) -> bool:
    session = instrument.nearest_session

    return (
        (range.from_t >= session.open_t and range.to_t < session.close_t)
        or range.from_t < session.open_t < range.to_t
        or range.from_t < session.close_t < range.to_t
    )
