from bars.models import BarSet, Bar, BarRange, Timeframe
from instruments.models import Instrument
from instruments import services as instrument_services
from common.schemas import Range
from . import crud
from . import utils
from ib.connector import ib_connector
from datetime import datetime, timedelta
from loguru import logger
import pytz
import math


async def get_bar_set(instrument: Instrument, timeframe: Timeframe) -> BarSet:
    return await BarSet.objects.select_related('instrument').get_or_create(
        instrument=instrument, timeframe=timeframe
    )


async def get_bars(bar_set: BarSet, range: Range) -> list[Bar]:
    existing_ranges = await BarRange.objects.filter(bar_set=bar_set).all()
    missing_ranges = _calculate_missing_ranges(range, existing_ranges)
    missing_ranges = _split_ranges(missing_ranges, bar_set.timeframe, 100)
    instrument = bar_set.instrument
    live_bar = None

    for missing_range in missing_ranges:
        is_overlap_session = await instrument_services.is_overlap_open_session(
            instrument, missing_range
        )

        # If missing range doesn't overlap with open session range
        if not is_overlap_session:
            # Extend missing range to overlap possible gaps in db
            missing_range.from_dt -= timedelta(days=1, seconds=1)
            missing_range.to_dt += timedelta(days=1, seconds=1)

        logger.debug(
            f'Missing bars in range. Retreiving from origin... '
            f'{instrument.exchange}:{instrument.symbol}, {bar_set.timeframe}, {missing_range}'
        )

        try:
            origin_bars = await _get_bars_from_origin(bar_set, missing_range)

            if (
                is_overlap_session
                and origin_bars
                and await get_latest_timestamp(bar_set) < origin_bars[-1].t
            ):
                live_bar = origin_bars[-1]
                origin_bars.remove(live_bar)

            await crud.add_bars(bar_set, origin_bars)

        except Exception as e:
            logger.debug(e)

    bars = await crud.get_bars(bar_set, range)
    if live_bar:
        bars.append(live_bar)

    return bars


async def get_latest_timestamp(bar_set: BarSet) -> datetime:
    latest_ts = await Bar.objects.filter(bar_set=bar_set).max('timestamp')
    return latest_ts or pytz.utc.localize(datetime.min)


async def _get_bars_from_origin(bar_set: BarSet, range: Range) -> list[Bar]:
    bars = await ib_connector.get_historical_bars(bar_set, range)
    instrument = bar_set.instrument

    if bars:
        logger.debug(
            f'Received bars from origin. '
            f'{instrument.exchange}:{instrument.symbol}, {bar_set.timeframe}, {range}'
        )
    else:
        logger.debug(
            f'No bars from origin. '
            f'{instrument.exchange}:{instrument.symbol}, {bar_set.timeframe}, {range}'
        )

    return bars


def _calculate_missing_ranges(
    within_range: Range, existing_ranges: list[BarRange]
) -> list[Range]:
    missing_ranges = []
    next_from_dt = within_range.from_dt

    for range in existing_ranges:
        if range.to_dt > within_range.from_dt and range.from_dt < within_range.to_dt:
            if range.from_dt > next_from_dt < within_range.to_dt:
                missing_ranges.append(Range(from_dt=next_from_dt, to_dt=range.from_dt))

            next_from_dt = range.to_dt

    if next_from_dt < within_range.to_dt:
        missing_ranges.append(Range(from_dt=next_from_dt, to_dt=within_range.to_dt))

    return missing_ranges


def _split_ranges(
    ranges: list[Range], timeframe: Timeframe, length: int
) -> list[Range]:
    splitted_ranges = []
    step_size = utils.get_step_size(timeframe)

    for range_to_split in ranges:
        bar_count = math.ceil(
            (range_to_split.to_dt - range_to_split.from_dt) / step_size
        )
        part_count = math.ceil(bar_count / length)

        to_dt = range_to_split.to_dt
        for _ in range(part_count):
            from_dt = to_dt - length * step_size
            if from_dt < range_to_split.from_dt:
                from_dt = range_to_split.from_dt

            splitted_range = Range(from_dt=from_dt, to_dt=to_dt)
            splitted_ranges.append(splitted_range)
            to_dt = from_dt - step_size

    return splitted_ranges
