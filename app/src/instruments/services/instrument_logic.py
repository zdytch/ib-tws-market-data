from instruments.models import Instrument, Exchange, TradingSession, InstrumentType
from instruments.repositories import instrument_repo, trading_session_repo
from common.schemas import Range
from ib.connector import ib_connector
from datetime import datetime
import pytz


async def get_instrument(ticker: str) -> Instrument:
    exchange, symbol = _split_ticker(ticker)

    try:
        instrument = await instrument_repo.get(symbol=symbol, exchange=exchange)
    except instrument_repo.NoResult:
        info = await ib_connector.get_instrument_info(symbol, exchange)
        instrument = await instrument_repo.create(
            symbol=info.symbol,
            ib_symbol=info.ib_symbol,
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
    return await instrument_repo.search_by_symbol_and_type(search, type)


async def search_instruments(symbol: str) -> list[Instrument]:
    instruments = []
    infos = await ib_connector.search_instrument_info(symbol)

    for info in infos:
        instrument = Instrument(
            symbol=info.symbol,
            ib_symbol=info.ib_symbol,
            exchange=info.exchange,
            type=info.type,
            description=info.description,
            tick_size=info.tick_size,
            multiplier=info.multiplier,
        )
        instruments.append(instrument)

    return instruments


async def get_trading_session(instrument: Instrument) -> TradingSession:
    session, _ = await trading_session_repo.get_or_create(instrument=instrument)

    if not _is_session_up_to_date(session):
        info = await ib_connector.get_instrument_info(
            instrument.symbol, instrument.exchange
        )
        session = await trading_session_repo.update(
            session,
            open_dt=info.trading_range.from_dt,
            close_dt=info.trading_range.to_dt,
        )

    return session


async def is_overlap_open_session(instrument: Instrument, range: Range) -> bool:
    session = await get_trading_session(instrument)

    return (
        (range.from_dt >= session.open_dt and range.to_dt < session.close_dt)
        or range.from_dt < session.open_dt < range.to_dt
        or range.from_dt < session.close_dt < range.to_dt
    )


async def is_session_open(instrument: Instrument) -> bool:
    session = await get_trading_session(instrument)

    return session.open_dt <= datetime.now(pytz.utc) < session.close_dt


def _is_session_up_to_date(session: TradingSession) -> bool:
    return session.close_dt > datetime.now(pytz.utc)


def _split_ticker(ticker: str) -> tuple[Exchange, str]:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    return (exchange, symbol)
