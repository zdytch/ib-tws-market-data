from instruments.models import Instrument, Exchange, Session
from ormar import NoMatch
from ib.connector import ib_connector
from time import time
from loguru import logger


async def get_instrument(symbol: str, exchange: Exchange) -> Instrument:
    try:
        instrument = await Instrument.objects.get(symbol=symbol, exchange=exchange)

    except NoMatch:
        try:
            instrument = await _get_instrument_from_origin(symbol, exchange)
            await instrument.save()
        except Exception as e:
            logger.debug(e)

    return instrument


async def get_session(instrument: Instrument) -> Session:
    session = await Session.objects.get_or_create(instrument)

    if not _is_session_up_to_date(session):
        session = await _get_session_from_origin(instrument)
        await session.update()

    return session


async def _get_instrument_from_origin(symbol: str, exchange: Exchange) -> Instrument:
    instrument = await ib_connector.get_instrument(symbol, exchange)

    logger.debug(f'Received instrument from origin: {instrument}')

    return instrument


async def _get_session_from_origin(instrument: Instrument) -> Session:
    session = await ib_connector.get_nearest_trading_session(instrument)

    logger.debug(f'Received session from origin: {session}')

    return session


def _is_session_open(instrument: Instrument) -> bool:
    return (
        instrument.nearest_session.open_t
        <= int(time())
        < instrument.nearest_session.close_t
    )


def _is_session_up_to_date(session: Session) -> bool:
    return session.close_t > int(time())