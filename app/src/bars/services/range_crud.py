from bars.schemas import Range, Timeframe
from instruments.schemas import Instrument
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from config.db import database


async def create_range(
    instrument: Instrument, timeframe: Timeframe, range: Range
) -> None:
    collection = _get_collection(instrument, timeframe)

    await collection.insert_one(range.dict())

    await _perform_defragmentation(collection)


async def read_ranges(instrument: Instrument, timeframe: Timeframe) -> list[Range]:
    collection = _get_collection(instrument, timeframe)

    return [Range(**dic) for dic in await collection.find().to_list(999)]


async def _perform_defragmentation(collection: Collection) -> None:
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


def _get_collection(instrument: Instrument, timeframe: Timeframe) -> Collection:
    name = f'{instrument.symbol}_{instrument.exchange}_{timeframe}_ranges'.lower()
    collection = database[name]

    return collection
