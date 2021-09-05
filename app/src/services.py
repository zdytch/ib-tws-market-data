from schemas import (
    Timeframe,
    InstrumentType,
    Exchange,
    Bar,
    ChartData,
    Range,
    Instrument,
)
from ib_connector import IBConnector
from datetime import datetime
import pytz
import cache
from loguru import logger

ibc = IBConnector()


async def get_historical_bars(
    ticker: str, timeframe: Timeframe, from_t: int, to_t: int
) -> list[Bar]:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)
    type = _get_instrument_type_by_exchange(exchange)
    instrument = Instrument(
        symbol=symbol, exchange=exchange, timeframe=timeframe, type=type
    )
    range = Range(from_t=from_t, to_t=to_t)

    cache_ranges = await cache.get_ranges(instrument)
    missing_ranges = _calculate_missing_ranges(range, cache_ranges)

    for missing_range in missing_ranges:
        logger.debug(
            f'Missing bars in cache. Retreiving from origin... Instrument: {instrument}. Range: {missing_range}'
        )

        origin_bars = await _get_bars_from_origin(instrument, missing_range)
        if origin_bars:
            await cache.save_bars(instrument, missing_range, origin_bars)

    return await cache.get_bars(instrument, range)


def get_chart_data_from_bars(bars: list[Bar]) -> ChartData:
    chart_data = ChartData()

    for bar in bars:
        chart_data.o.append(bar.o)
        chart_data.h.append(bar.h)
        chart_data.l.append(bar.l)
        chart_data.c.append(bar.c)
        chart_data.v.append(bar.v)
        chart_data.t.append(bar.t)
    if all(value for value in chart_data.dict().values()):
        chart_data.s = 'ok'

    return chart_data


async def _get_bars_from_origin(instrument: Instrument, range: Range) -> list[Bar]:
    from_dt = datetime.fromtimestamp(range.from_t, pytz.utc)
    to_dt = datetime.fromtimestamp(range.to_t, pytz.utc)

    bars = await ibc.get_historical_bars(instrument, from_dt, to_dt)

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


def _get_instrument_type_by_exchange(exchange: Exchange) -> InstrumentType:
    if exchange in (Exchange.NASDAQ, Exchange.NYSE):
        instrument_type = InstrumentType.STOCK
    elif exchange in (Exchange.GLOBEX, Exchange.ECBOT, Exchange.NYMEX):
        instrument_type = InstrumentType.FUTURE
    else:
        raise ValueError(f'Cannot get instrument type, exchange unknown: {exchange}')

    return instrument_type
