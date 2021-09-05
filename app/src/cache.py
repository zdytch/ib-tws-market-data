from schemas import Instrument, Bar, Range
from config.db import database
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from pymongo.errors import BulkWriteError
from loguru import logger


async def get_bars(instrument: Instrument, range: Range) -> list[Bar]:
    bars = []
    collection, _ = _get_collections(instrument)

    cursor = collection.find({'t': {'$gte': range.from_t, '$lte': range.to_t}}).sort(
        't'
    )
    for mongo_bar in await cursor.to_list(999):
        bar = Bar(**mongo_bar)
        bars.append(bar)

    return bars


async def save_bars(instrument: Instrument, range: Range, bars: list[Bar]) -> None:
    if bars:
        collection, _ = _get_collections(instrument)
        try:
            await collection.insert_many([bar.dict() for bar in bars])
        except BulkWriteError:
            pass

        await save_range(instrument, range)

        logger.debug(f'Bars saved to cache. Instrument: {instrument}. Range: {range}')


async def get_ranges(instrument: Instrument) -> list[Range]:
    _, collection = _get_collections(instrument)
    return [Range(**dic) for dic in await collection.find().to_list(999)]


async def save_range(instrument: Instrument, range: Range) -> None:
    _, collection = _get_collections(instrument)

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


def _get_collections(instrument: Instrument) -> tuple[Collection, Collection]:
    name = f'{instrument.symbol}_{instrument.exchange}_{instrument.timeframe}'.lower()
    bar_col_name = f'{name}_bars'
    range_col_name = f'{name}_ranges'

    bar_collection = database[bar_col_name]
    bar_collection.create_index('t', unique=True)
    range_collection = database[range_col_name]

    return bar_collection, range_collection
