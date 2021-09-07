from instruments.schemas import Instrument, Exchange
from ib.connector import ib_connector
from time import time
from . import crud
from loguru import logger


async def get_instrument(ticker: str) -> Instrument:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    try:
        instrument = await crud.read_instrument(symbol, exchange)
    except:
        try:
            instrument = await _get_instrument_from_origin(symbol, exchange)
            await crud.create_instrument(instrument)

        except Exception as e:
            logger.debug(e)

    return instrument


async def _get_instrument_from_origin(symbol: str, exchange: Exchange) -> Instrument:
    instrument = await ib_connector.get_instrument(symbol, exchange)

    logger.debug(f'Received instrument from origin: {instrument}')

    return instrument


def _is_session_open(instrument: Instrument) -> bool:
    return (
        instrument.nearest_session.open_t
        <= int(time())
        < instrument.nearest_session.close_t
    )


def _is_session_up_to_date(instrument: Instrument) -> bool:
    return instrument.nearest_session.close_t > int(time())
