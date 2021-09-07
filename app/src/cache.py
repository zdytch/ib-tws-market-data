from instruments.schemas import Instrument, Exchange
from bars.schemas import Bar, Timeframe, Range
from config.db import database
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from pymongo.errors import BulkWriteError
from loguru import logger


async def get_bars(
    instrument: Instrument, timeframe: Timeframe, range: Range
) -> list[Bar]:
    bars = []
    collection, _ = _get_collections(instrument, timeframe)

    cursor = collection.find({'t': {'$gte': range.from_t, '$lte': range.to_t}}).sort(
        't'
    )
    for mongo_bar in await cursor.to_list(999):
        bar = Bar(**mongo_bar)
        bars.append(bar)

    return bars


async def get_last_timestamp(instrument: Instrument, timeframe: Timeframe) -> int:
    # TODO: Find better approach
    ts = 0
    collection, _ = _get_collections(instrument, timeframe)
    bar_as_list = await collection.find().sort('t', -1).limit(1).to_list(1)

    if bar_as_list:
        mongo_bar = bar_as_list[0]
        ts = mongo_bar['t']

    return ts


async def save_bars(
    instrument: Instrument, timeframe: Timeframe, bars: list[Bar]
) -> None:
    if bars:
        collection, _ = _get_collections(instrument, timeframe)
        try:
            await collection.insert_many([bar.dict() for bar in bars])
        except BulkWriteError:
            pass

        min_ts = min(bars, key=lambda bar: bar.t).t
        max_ts = max(bars, key=lambda bar: bar.t).t
        range = Range(from_t=min_ts, to_t=max_ts)
        await save_range(instrument, timeframe, range)

        logger.debug(f'Bars saved to cache. Instrument: {instrument}. Range: {range}')


async def get_ranges(instrument: Instrument, timeframe: Timeframe) -> list[Range]:
    _, collection = _get_collections(instrument, timeframe)
    return [Range(**dic) for dic in await collection.find().to_list(999)]


async def save_range(
    instrument: Instrument, timeframe: Timeframe, range: Range
) -> None:
    _, collection = _get_collections(instrument, timeframe)

    await collection.insert_one(range.dict())

    await _perform_range_defragmentation(collection)


async def _perform_range_defragmentation(
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


def _get_collections(
    instrument: Instrument, timeframe: Timeframe
) -> tuple[Collection, Collection]:
    name = f'{instrument.symbol}_{instrument.exchange}_{timeframe}'.lower()
    bar_col_name = f'{name}_bars'
    range_col_name = f'{name}_ranges'

    bar_collection = database[bar_col_name]
    bar_collection.create_index('t', unique=True)
    range_collection = database[range_col_name]

    return bar_collection, range_collection
