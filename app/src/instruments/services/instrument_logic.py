from instruments.models import Instrument, Exchange, TradingSession, InstrumentType
from common.schemas import Range
from ormar import NoMatch
from ib.connector import ib_connector
from time import time


async def get_instrument(ticker: str) -> Instrument:
    exchange, symbol = _split_ticker(ticker)

    try:
        instrument = await Instrument.objects.get(symbol=symbol, exchange=exchange)
    except NoMatch:
        info = await ib_connector.get_instrument_info(symbol, exchange)
        instrument = await Instrument.objects.create(
            symbol=info.symbol,
            exchange=info.exchange,
            type=info.type,
            description=info.description,
            tick_size=info.tick_size,
            multiplier=info.multiplier,
        )

    return instrument


async def get_instrument_list(
    search: str = None,
    type: InstrumentType = None,
) -> list[Instrument]:
    instruments = Instrument.objects
    if search:
        instruments = instruments.filter(symbol__icontains=search)
    if type:
        instruments = instruments.filter(type=type)

    return await instruments.all()


async def get_session(instrument: Instrument) -> TradingSession:
    session = await TradingSession.objects.get_or_create(instrument=instrument)

    if not _is_session_up_to_date(session):
        info = await ib_connector.get_instrument_info(
            instrument.symbol, instrument.exchange
        )
        session.open_t = info.trading_range.from_t
        session.close_t = info.trading_range.to_t
        await session.update(['open_t', 'close_t'])

    return session


async def is_overlap_open_session(instrument: Instrument, range: Range) -> bool:
    session = await get_session(instrument)

    return (
        (range.from_t >= session.open_t and range.to_t < session.close_t)
        or range.from_t < session.open_t < range.to_t
        or range.from_t < session.close_t < range.to_t
    )


async def is_session_open(instrument: Instrument) -> bool:
    session = await get_session(instrument)

    return session.open_t <= int(time()) < session.close_t


def _is_session_up_to_date(session: TradingSession) -> bool:
    return session.close_t > int(time())


def _split_ticker(ticker: str) -> tuple[Exchange, str]:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    return (exchange, symbol)
