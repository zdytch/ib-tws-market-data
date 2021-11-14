from bars.models import BarSet, Bar
from common.schemas import Range
from sqlalchemy.ext.asyncio import AsyncSession
from instruments import services as instrument_services
from ib.connector import ib_connector
from datetime import timedelta
from loguru import logger
from . import bar_crud, bar_range_crud, bar_range_logic


async def get_historical_bars(
    session: AsyncSession, bar_set: BarSet, range: Range
) -> list[Bar]:
    existing_ranges = await bar_range_crud.get_bar_ranges(session, bar_set)
    missing_ranges = bar_range_logic.calculate_missing_ranges(range, existing_ranges)
    missing_ranges = bar_range_logic.split_ranges(
        missing_ranges, bar_set.timeframe, 100
    )
    instrument = bar_set.instrument
    live_bar = None

    for missing_range in missing_ranges:
        is_overlap_session = await instrument_services.is_overlap_open_session(
            instrument, missing_range
        )
        latest_ts = await bar_crud.get_latest_timestamp(session, bar_set)

        # If missing range doesn't overlap with open session range
        if not is_overlap_session:
            # Extend missing range to overlap possible gaps in db
            missing_range.from_dt -= timedelta(days=1, seconds=1)
            missing_range.to_dt += timedelta(days=1, seconds=1)

        logger.debug(
            f'Missing bars in range. Retreiving from origin... '
            f'{instrument.exchange}:{instrument.symbol}, {bar_set.timeframe}, {missing_range}'
        )

        origin_bars = await _get_bars_from_origin(bar_set, missing_range)

        if (
            is_overlap_session
            and origin_bars
            and latest_ts
            and latest_ts < origin_bars[-1].timestamp
        ):
            live_bar = origin_bars[-1]
            origin_bars.remove(live_bar)

        await bar_crud.bulk_save_bars(session, bar_set, origin_bars)

    bars = await bar_crud.get_bars(session, bar_set, range)
    if live_bar:
        bars.append(live_bar)

    return bars


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
