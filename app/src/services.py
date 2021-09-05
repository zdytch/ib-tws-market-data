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
from config.db import database
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from pymongo.errors import BulkWriteError
import pytz

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

    cache_ranges = await _get_ranges_from_cache(instrument)
    missing_ranges = _get_missing_ranges(range, cache_ranges)

    for missing_range in missing_ranges:
        origin_bars = await _get_bars_from_ib(instrument, missing_range)
        if origin_bars:
            await _save_bars_to_cache(instrument, missing_range, origin_bars)

    return await _get_bars_from_cache(instrument, range)


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


async def _get_bars_from_cache(instrument: Instrument, range: Range) -> list[Bar]:
    bars = []
    collection, _ = _get_collections(instrument)

    cursor = collection.find({'t': {'$gte': range.from_t, '$lte': range.to_t}}).sort(
        't'
    )
    for mongo_bar in await cursor.to_list(999):
        bar = Bar(**mongo_bar)
        bars.append(bar)

    return bars


async def _get_ranges_from_cache(instrument: Instrument) -> list[Range]:
    _, collection = _get_collections(instrument)
    return [Range(**dic) for dic in await collection.find().to_list(999)]


async def _save_bars_to_cache(
    instrument: Instrument, range: Range, bars: list[Bar]
) -> None:
    if bars:
        collection, _ = _get_collections(instrument)

        try:
            await collection.insert_many([bar.dict() for bar in bars])
        except BulkWriteError:
            pass

        await _save_range_to_cache(instrument, range)


async def _get_bars_from_ib(instrument: Instrument, range: Range) -> list[Bar]:
    from_dt = datetime.fromtimestamp(range.from_t, pytz.utc)
    to_dt = datetime.fromtimestamp(range.to_t, pytz.utc)

    return await ibc.get_historical_bars(instrument, from_dt, to_dt)


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


async def _save_range_to_cache(instrument: Instrument, range: Range) -> None:
    _, collection = _get_collections(instrument)

    await collection.insert_one(range.dict())

    await _perform_cached_range_defragmentation(collection)


async def _perform_cached_range_defragmentation(
    collection: Collection,
) -> None:
    # TODO: Use mongo aggregation here
    in_progress = True
    while in_progress:
        try:
            ranges = [Range(**dic) for dic in await collection.find().to_list(999)]

            for range in ranges:
                for compare_range in ranges:
                    if compare_range is not range and (
                        range.from_t <= compare_range.from_t <= range.to_t
                        or range.from_t <= compare_range.to_t <= range.to_t
                    ):
                        min_t = min((compare_range.from_t, range.from_t))
                        max_t = max((compare_range.to_t, range.to_t))

                        # TODO: Delete by id
                        await collection.delete_many(
                            {'from_t': {'$in': [compare_range.from_t, range.from_t]}}
                        )
                        await collection.insert_one({'from_t': min_t, 'to_t': max_t})

                        raise StopIteration

            in_progress = False

        except StopIteration:
            pass


def _get_collections(instrument: Instrument) -> tuple[Collection, Collection]:
    name_base = (
        f'{instrument.symbol}_{instrument.exchange}_{instrument.timeframe}'.lower()
    )
    bar_col_name = f'{name_base}_bars'
    range_col_name = f'{name_base}_ranges'

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
