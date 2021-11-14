from instruments.models import Instrument, Exchange, InstrumentType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal


async def create_instrument(
    session: AsyncSession,
    symbol: str,
    ib_symbol: str,
    exchange: Exchange,
    type: InstrumentType,
    description: str,
    tick_size: Decimal,
    multiplier: Decimal,
) -> Instrument:
    instrument = Instrument(
        symbol=symbol,
        ib_symbol=ib_symbol,
        exchange=exchange,
        type=type,
        description=description,
        tick_size=tick_size,
        multiplier=multiplier,
    )
    session.add(instrument)

    await session.commit()

    return instrument


async def get_instrument(
    session: AsyncSession, symbol: str, exchange: Exchange
) -> Instrument:
    query = select(Instrument).filter_by(symbol=symbol, exchange=exchange)

    return (await session.execute(query)).scalar_one()


async def filter_instruments(
    session: AsyncSession, symbol: str = None, type: InstrumentType = None
) -> list[Instrument]:
    query = select(Instrument)

    if symbol:
        query = query.where(Instrument.symbol.contains(symbol))  # type: ignore
    if type:
        query = query.filter_by(type=type)

    return (await session.execute(query)).scalars().all()
