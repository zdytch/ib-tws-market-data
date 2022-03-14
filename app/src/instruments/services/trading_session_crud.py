from instruments.models import TradingSession, Instrument
from config.db import DB
from sqlalchemy.future import select
from sqlalchemy.orm.exc import NoResultFound


async def get_or_create_trading_session(
    db: DB, instrument: Instrument
) -> TradingSession:
    try:
        query = select(TradingSession).filter_by(instrument=instrument)
        trading_session = (await db.execute(query)).scalar_one()

    except NoResultFound:
        trading_session = TradingSession(instrument_id=instrument.id)
        db.add(trading_session)

        await db.commit()

    return trading_session
