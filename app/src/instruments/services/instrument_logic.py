from instruments.models import Instrument, Exchange
from ormar import NoMatch
from ib.connector import ib_connector
from time import time
from loguru import logger


async def get_or_create_instrument(ticker: str) -> Instrument:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    try:
        instrument = await Instrument.objects.get(symbol=symbol, exchange=exchange)

    except NoMatch:
        try:
            instrument = await _get_instrument_from_origin(symbol, exchange)
            await instrument.save()
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
