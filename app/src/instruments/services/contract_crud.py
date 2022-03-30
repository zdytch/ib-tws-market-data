from instruments.models import Contract, Instrument, Exchange, InstrumentType
from config.db import DB
from sqlalchemy.future import select
from datetime import datetime
from decimal import Decimal


async def create_contract(
    db: DB,
    instrument: Instrument,
    ib_id: int,
    expiration: datetime,
) -> Contract:
    contract = Contract(
        instrument_id=instrument.id,
        ib_id=ib_id,
        expiration=expiration,
    )
    db.add(contract)

    await db.commit()

    return contract
