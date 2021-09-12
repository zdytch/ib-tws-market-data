from instruments.models import Instrument, Exchange, TradingSession
from ormar import NoMatch
from ib.connector import ib_connector
from time import time
from loguru import logger


async def get_instrument(symbol: str, exchange: Exchange) -> Instrument:
    try:
        instrument = await Instrument.objects.get(symbol=symbol, exchange=exchange)

    except NoMatch:
        try:
            info = await ib_connector.get_instrument_info(symbol, exchange)
            instrument = await Instrument.objects.create(
                symbol=info.symbol,
                exchange=info.exchange,
                type=info.type,
                description=info.description,
                tick_size=info.tick_size,
                multiplier=info.multiplier,
            )
        except Exception as e:
            logger.debug(e)

    return instrument


async def get_session(instrument: Instrument) -> TradingSession:
    session = await TradingSession.objects.get_or_create(instrument=instrument)

    if not _is_session_up_to_date(session):
        info = await ib_connector.get_instrument_info(
            instrument.symbol, instrument.exchange
        )
        session.open_t = info.trading_session.from_t
        session.close_t = info.trading_session.to_t
        await session.update(['open_t', 'close_t'])

    return session


async def is_overlap_open_session(
    instrument: Instrument, from_t: int, to_t: int
) -> bool:
    session = await get_session(instrument)

    return (
        (from_t >= session.open_t and to_t < session.close_t)
        or from_t < session.open_t < to_t
        or from_t < session.close_t < to_t
    )


def _is_session_open(instrument: Instrument) -> bool:
    return (
        instrument.nearest_session.open_t
        <= int(time())
        < instrument.nearest_session.close_t
    )


def _is_session_up_to_date(session: TradingSession) -> bool:
    return session.close_t > int(time())
