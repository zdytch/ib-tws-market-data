from instruments.schemas import Instrument, Exchange
from config.db import database


async def create_instrument(instrument: Instrument) -> None:
    collection = database.instruments
    collection.create_index('symbol', 'exchange', unique=True)

    await collection.insert_one(instrument.dict())


async def read_instrument(symbol: str, exchange: Exchange) -> Instrument:
    collection = database.instruments
    instrument_dict = await collection.find_one(
        {'symbol': symbol, 'exchange': exchange}
    )

    return Instrument(**instrument_dict)


async def update_instrument(instrument: Instrument, fields: dict) -> Instrument:
    collection = database.instruments
    instrument_dict = await collection.update_one(
        {'symbol': instrument.symbol, 'exchange': instrument.exchange},
        {'$set': fields},
    )

    return Instrument(**instrument_dict)
