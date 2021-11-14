from instruments.models import TradingSession, Instrument
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.exc import NoResultFound


async def get_or_create_trading_session(
    session: AsyncSession, instrument: Instrument
) -> TradingSession:
    try:
        query = select(TradingSession).filter_by(instrument=instrument)
        trading_session = (await session.execute(query)).scalar_one()

    except NoResultFound:
        trading_session = TradingSession(instrument_id=instrument.id)
        session.add(trading_session)

        await session.commit()

        # query = select(TradingSession).filter_by(instrument=instrument)
        # trading_session = (await session.execute(query)).scalar_one()

    return trading_session
