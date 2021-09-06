from schemas import (
    Timeframe,
    Exchange,
    Bar,
    ChartData,
    Range,
    Instrument,
    BarList,
    InstrumentType,
)
from ib_connector import IBConnector
from datetime import datetime
from time import time
from decimal import Decimal
import pytz
import cache
from loguru import logger

ibc = IBConnector()


async def get_instrument(ticker: str) -> Instrument:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    try:
        instrument = await cache.get_instrument(symbol, exchange)
    except:
        try:
            instrument = await _get_instrument_from_origin(symbol, exchange)
            await cache.save_instrument(instrument)

        except Exception as e:
            logger.debug(e)

    return instrument


async def get_bar_list(
    ticker: str, timeframe: Timeframe, from_t: int, to_t: int
) -> BarList:
    instrument = await get_instrument(ticker)
    range = Range(from_t=from_t, to_t=to_t)

    cache_ranges = await cache.get_ranges(instrument, timeframe)
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
            await cache.save_bars(instrument, timeframe, origin_bars)
        except Exception as e:
            logger.debug(e)

    bars = await cache.get_bars(instrument, timeframe, range)

    return BarList(instrument=instrument, timeframe=timeframe, bars=bars)


async def bar_list_to_chart_data(data: BarList) -> ChartData:
    chart_data = ChartData()

    for bar in data.bars:
        chart_data.o.append(bar.o)
        chart_data.h.append(bar.h)
        chart_data.l.append(bar.l)
        chart_data.c.append(bar.c)
        chart_data.v.append(bar.v)
        chart_data.t.append(bar.t)

    if data.bars:
        chart_data.s = 'ok'
    else:
        last_ts = await cache.get_last_timestamp(data.instrument, data.timeframe)
        chart_data.next_time = last_ts

    return chart_data


async def get_info(ticker: str) -> dict:
    instrument = await get_instrument(ticker)
    instrument_type = _instrument_type_to_chart(instrument.type)
    timezone, session = _exchange_schedule_to_chart(instrument.exchange)
    price_scale = 10 ** abs(
        Decimal(instrument.tick_size).normalize().as_tuple().exponent
    )
    min_movement = int(instrument.tick_size * price_scale)

    return {
        'name': ticker,
        'ticker': ticker,
        'type': instrument_type,
        'description': instrument.description,
        'exchange': instrument.exchange,
        'listed_exchange': instrument.exchange,
        'session': session,
        'timezone': timezone,
        'currency_code': 'USD',
        'has_daily': True,
        'has_intraday': True,
        'minmov': min_movement,
        'pricescale': price_scale,
    }


def get_config() -> dict:
    return {
        'supported_resolutions': ['1', '5', '30', '1D'],
        'supports_search': True,
        'supports_group_request': False,
        'supports_marks': False,
        'supports_timescale_marks': False,
    }


async def _get_instrument_from_origin(symbol: str, exchange: Exchange) -> Instrument:
    instrument = await ibc.get_instrument(symbol, exchange)

    logger.debug(f'Received instrument from origin: {instrument}')

    return instrument


async def _get_bars_from_origin(
    instrument: Instrument, timeframe: Timeframe, range: Range
) -> list[Bar]:
    from_dt = datetime.fromtimestamp(range.from_t, pytz.utc)
    to_dt = datetime.fromtimestamp(range.to_t, pytz.utc)

    bars = await ibc.get_historical_bars(instrument, timeframe, from_dt, to_dt)

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


def _is_session_open(instrument: Instrument) -> bool:
    return (
        instrument.nearest_session.open_t
        <= int(time())
        < instrument.nearest_session.close_t
    )


def _is_session_up_to_date(instrument: Instrument) -> bool:
    return instrument.nearest_session.close_t > int(time())


def _instrument_type_to_chart(type: InstrumentType) -> str:
    if type == InstrumentType.STOCK:
        instrument_type = 'stock'
    elif type == InstrumentType.FUTURE:
        instrument_type = 'futures'
    else:
        raise ValueError(f'Cannot convert {type} to InstrumentType')

    return instrument_type


def _exchange_schedule_to_chart(exchange: Exchange) -> tuple[str, str]:
    if exchange in (Exchange.NASDAQ, Exchange.NYSE):
        tz_id = 'America/New_York'
        session = '0930-1600'
    elif exchange == Exchange.NYMEX:
        tz_id = 'America/New_York'
        session = '1800-1700'
    elif exchange == Exchange.GLOBEX:
        tz_id = 'America/Chicago'
        session = '1700-1600'
    elif exchange == Exchange.ECBOT:
        tz_id = 'America/Chicago'
        session = '1900-1320'
    else:
        raise ValueError(f'Cannot get schedule for exchange {exchange}')

    return tz_id, session
