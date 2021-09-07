from instruments.schemas import Instrument
from bars.schemas import Bar, Timeframe, Range
from . import range_crud
from config.db import database
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from pymongo.errors import BulkWriteError
from loguru import logger


async def create_bars(
    instrument: Instrument, timeframe: Timeframe, bars: list[Bar]
) -> None:
    if bars:
        collection = _get_collection(instrument, timeframe)
        try:
            await collection.insert_many([bar.dict() for bar in bars])
        except BulkWriteError:
            pass

        min_ts = min(bars, key=lambda bar: bar.t).t
        max_ts = max(bars, key=lambda bar: bar.t).t
        range = Range(from_t=min_ts, to_t=max_ts)
        await range_crud.create_range(instrument, timeframe, range)

        logger.debug(f'Bars created. Instrument: {instrument}. Range: {range}')


async def read_bars(
    instrument: Instrument, timeframe: Timeframe, range: Range
) -> list[Bar]:
    bars = []
    collection = _get_collection(instrument, timeframe)

    cursor = collection.find({'t': {'$gte': range.from_t, '$lte': range.to_t}}).sort(
        't'
    )
    for mongo_bar in await cursor.to_list(999):
        bar = Bar(**mongo_bar)
        bars.append(bar)

    return bars


async def get_last_bar_timestamp(instrument: Instrument, timeframe: Timeframe) -> int:
    # TODO: Find better approach
    t = 0
    collection = _get_collection(instrument, timeframe)
    bar_as_list = await collection.find().sort('t', -1).limit(1).to_list(1)

    if bar_as_list:
        mongo_bar = bar_as_list[0]
        t = mongo_bar['t']

    return t


def _get_collection(instrument: Instrument, timeframe: Timeframe) -> Collection:
    name = f'{instrument.symbol}_{instrument.exchange}_{timeframe}_bars'.lower()
    collection = database[name]
    collection.create_index('t', unique=True)

    return collection
