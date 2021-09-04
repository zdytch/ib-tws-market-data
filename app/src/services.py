from schemas import Timeframe, InstrumentType, Exchange, Bar, ChartData, Range
from ib_connector import IBConnector
from datetime import datetime
from config.db import database
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import BulkWriteError
import pytz

ibc = IBConnector()


async def get_historical_bars(
    ticker: str, timeframe: Timeframe, range: Range
) -> list[Bar]:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    cached_bars = await _get_bars_from_cache(symbol, exchange, timeframe, range)
    if not cached_bars:
        live_bars = await _get_bars_from_ib(symbol, exchange, timeframe, range)
        if live_bars:
            await _save_bars_to_cache(symbol, exchange, timeframe, range, live_bars)

    return await _get_bars_from_cache(symbol, exchange, timeframe, range)


def get_chart_data_from_bars(bar_list: list[Bar]) -> ChartData:
    chart_data = ChartData()

    for bar in bar_list:
        chart_data.o.append(bar.o)
        chart_data.h.append(bar.h)
        chart_data.l.append(bar.l)
        chart_data.c.append(bar.c)
        chart_data.v.append(bar.v)
        chart_data.t.append(bar.t)
    if all(value for value in chart_data.dict().values()):
        chart_data.s = 'ok'

    return chart_data


async def _get_bars_from_cache(
    symbol: str, exchange: Exchange, timeframe: Timeframe, range: Range
) -> list[Bar]:
    bars = []
    collection, _ = _get_collections(symbol, exchange, timeframe)

    cursor = collection.find({'t': {'$gte': range.from_t, '$lte': range.to_t}}).sort(
        't'
    )
    for mongo_bar in await cursor.to_list(999):
        bar = Bar(**mongo_bar)
        bars.append(bar)

    return bars


async def _save_bars_to_cache(
    symbol: str,
    exchange: Exchange,
    timeframe: Timeframe,
    range: Range,
    bars: list[Bar],
) -> None:
    if bars:
        collection, _ = _get_collections(symbol, exchange, timeframe)

        try:
            await collection.insert_many([bar.dict() for bar in bars])
        except BulkWriteError:
            pass

        await _save_range_to_cache(symbol, exchange, timeframe, range)


async def _get_bars_from_ib(
    symbol: str, exchange: Exchange, timeframe: Timeframe, range: Range
) -> list[Bar]:
    instrument_type = _get_instrument_type_by_exchange(Exchange(exchange))
    from_dt = datetime.fromtimestamp(range.from_t, pytz.utc)
    to_dt = datetime.fromtimestamp(range.to_t, pytz.utc)

    return await ibc.get_historical_bars(
        symbol, exchange, instrument_type, timeframe, from_dt, to_dt
    )


def _get_missing_ranges(within_range: Range, existing_ranges: list[Range]) -> list:
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


async def _save_range_to_cache(
    symbol: str, exchange: Exchange, timeframe: Timeframe, range: Range
) -> None:
    _, collection = _get_collections(symbol, exchange, timeframe)

    await collection.insert_one(**range)

    await _perform_cached_range_defragmentation(collection)


async def _perform_cached_range_defragmentation(
    collection: AsyncIOMotorCollection,
) -> None:
    # TODO: Use mongo aggregation here
    in_progress = True
    while in_progress:
        try:
            ranges = [
                Range(**dic) for dic in await collection.find().cursor.to_list(999)
            ]

            for range in ranges:
                for compare_range in ranges:
                    if compare_range is not range and (
                        range.from_t <= compare_range.from_t <= range.to_t
                        or range.from_t <= compare_range.to_t <= range.to_t
                    ):
                        min_t = min((compare_range.from_t, range.from_t))
                        max_t = max((compare_range.to_t, range.to_t))

                        await collection.delete_many(
                            {'from_t': {'$in': [compare_range.from_t, range.from_t]}}
                        )
                        await collection.insert_one({'from_t': min_t, 'to_t': max_t})

                        raise StopIteration

            in_progress = False

        except StopIteration:
            pass


def _get_collections(
    symbol: str, exchange: Exchange, timeframe: Timeframe
) -> tuple[AsyncIOMotorCollection, AsyncIOMotorCollection]:
    bar_col_name = f'{symbol.lower()}_{exchange.lower()}_{timeframe.lower()}_bars'
    range_col_name = f'{symbol.lower()}_{exchange.lower()}_{timeframe.lower()}_ranges'

    bar_collection = database[bar_col_name]
    bar_collection.create_index('t', unique=True)
    range_collection = database[range_col_name]

    return bar_collection, range_collection


def _get_instrument_type_by_exchange(exchange: Exchange) -> InstrumentType:
    if exchange in (Exchange.NASDAQ, Exchange.NYSE):
        instrument_type = InstrumentType.STOCK
    elif exchange in (Exchange.GLOBEX, Exchange.ECBOT, Exchange.NYMEX):
        instrument_type = InstrumentType.FUTURE
    else:
        raise ValueError(f'Cannot get instrument type, exchange unknown: {exchange}')

    return instrument_type
