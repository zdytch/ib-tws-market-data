from schemas import Timeframe, InstrumentType, Exchange, Bar, ChartData
from ib_connector import IBConnector
from datetime import datetime
from config.db import database
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import BulkWriteError
import pytz

ibc = IBConnector()


async def get_historical_bars(
    ticker: str, timeframe: Timeframe, from_ts: int, to_ts: int
) -> list[Bar]:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    cached_bars = await _get_bars_from_cache(
        symbol, exchange, timeframe, from_ts, to_ts
    )
    if not cached_bars:
        live_bars = await _get_bars_from_ib(symbol, exchange, timeframe, from_ts, to_ts)
        if live_bars:
            await _save_bars_to_cache(
                symbol, exchange, timeframe, from_ts, to_ts, live_bars
            )

    return await _get_bars_from_cache(symbol, exchange, timeframe, from_ts, to_ts)


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
    symbol: str, exchange: Exchange, timeframe: Timeframe, from_ts: int, to_ts: int
) -> list[Bar]:
    bars = []
    collection, _ = _get_collections(symbol, exchange, timeframe)

    cursor = collection.find({'t': {'$gte': from_ts, '$lte': to_ts}}).sort('t')
    for mongo_bar in await cursor.to_list(999):
        bar = Bar(**mongo_bar)
        bars.append(bar)

    return bars


async def _save_bars_to_cache(
    symbol: str,
    exchange: Exchange,
    timeframe: Timeframe,
    from_ts: int,
    to_ts: int,
    bars: list[Bar],
) -> None:
    if bars:
        collection, _ = _get_collections(symbol, exchange, timeframe)

        try:
            await collection.insert_many([bar.dict() for bar in bars])
        except BulkWriteError:
            pass

        await _save_chunk(symbol, exchange, timeframe, from_ts, to_ts)


async def _get_bars_from_ib(
    symbol: str, exchange: Exchange, timeframe: Timeframe, from_ts: int, to_ts: int
) -> list[Bar]:
    instrument_type = _get_instrument_type_by_exchange(Exchange(exchange))
    from_dt = datetime.fromtimestamp(from_ts, pytz.utc)
    to_dt = datetime.fromtimestamp(to_ts, pytz.utc)

    return await ibc.get_historical_bars(
        symbol, exchange, instrument_type, timeframe, from_dt, to_dt
    )


async def _save_chunk(
    symbol: str, exchange: Exchange, timeframe: Timeframe, from_ts: int, to_ts: int
) -> None:
    _, collection = _get_collections(symbol, exchange, timeframe)

    await collection.insert_one({'from_ts': from_ts, 'to_ts': to_ts})

    await _perform_chunk_defragmentation(collection)


async def _perform_chunk_defragmentation(collection: AsyncIOMotorCollection) -> None:
    # TODO: Use mongo aggregation here
    in_progress = True
    while in_progress:
        try:
            cursor = collection.find()
            chunks = await cursor.to_list(999)

            for chunk in chunks:
                for compare_chunk in chunks:
                    if compare_chunk is not chunk and (
                        chunk['from_ts'] <= compare_chunk['from_ts'] <= chunk['to_ts']
                        or chunk['from_ts'] <= compare_chunk['to_ts'] <= chunk['to_ts']
                    ):
                        min_ts = min((compare_chunk['from_ts'], chunk['from_ts']))
                        max_ts = max((compare_chunk['to_ts'], chunk['to_ts']))

                        await collection.insert_one(
                            {'from_ts': min_ts, 'to_ts': max_ts}
                        )
                        await collection.delete_many(
                            {'_id': {'$in': [compare_chunk['_id'], chunk['_id']]}}
                        )

                        raise StopIteration

            in_progress = False

        except StopIteration:
            pass


def _get_collections(
    symbol: str, exchange: Exchange, timeframe: Timeframe
) -> tuple[AsyncIOMotorCollection, AsyncIOMotorCollection]:
    bar_col_name = f'{symbol.lower()}_{exchange.lower()}_{timeframe.lower()}_bars'
    chunk_col_name = f'{symbol.lower()}_{exchange.lower()}_{timeframe.lower()}_chunks'

    bar_collection = database[bar_col_name]
    bar_collection.create_index('t', unique=True)
    chunk_collection = database[chunk_col_name]

    return bar_collection, chunk_collection


def _get_instrument_type_by_exchange(exchange: Exchange) -> InstrumentType:
    if exchange in (Exchange.NASDAQ, Exchange.NYSE):
        instrument_type = InstrumentType.STOCK
    elif exchange in (Exchange.GLOBEX, Exchange.ECBOT, Exchange.NYMEX):
        instrument_type = InstrumentType.FUTURE
    else:
        raise ValueError(f'Cannot get instrument type, exchange unknown: {exchange}')

    return instrument_type
