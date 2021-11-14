from instruments.models import Instrument, TradingSession
from common.schemas import Range
from config.db import DB
from ib.connector import ib_connector
from datetime import datetime
import pytz
from . import trading_session_crud


async def get_nearest_trading_session(db: DB, instrument: Instrument) -> TradingSession:
    trading_session = await trading_session_crud.get_or_create_trading_session(
        db, instrument
    )

    if not is_session_up_to_date(trading_session):
        info = await ib_connector.get_instrument_info(
            instrument.symbol, instrument.exchange
        )
        trading_session.open_dt = info.trading_range.from_dt
        trading_session.close_dt = info.trading_range.to_dt

        await db.commit()

    return trading_session


async def is_overlap_open_session(db: DB, instrument: Instrument, range: Range) -> bool:
    trading_session = await get_nearest_trading_session(db, instrument)

    return (
        (
            range.from_dt >= trading_session.open_dt
            and range.to_dt < trading_session.close_dt
        )
        or range.from_dt < trading_session.open_dt < range.to_dt
        or range.from_dt < trading_session.close_dt < range.to_dt
    )


async def is_session_open(db: DB, instrument: Instrument) -> bool:
    trading_session = await get_nearest_trading_session(db, instrument)

    return trading_session.open_dt <= datetime.now(pytz.utc) < trading_session.close_dt


def is_session_up_to_date(session: TradingSession) -> bool:
    return session.close_dt > datetime.now(pytz.utc)
