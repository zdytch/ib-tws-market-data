from ..models import Alert
from config.db import DB
from sqlmodel import select
from sqlalchemy.orm import joinedload
from instruments import services as instrument_services
from decimal import Decimal


async def get_alert_list(db: DB) -> list[Alert]:
    query = select(Alert).options(joinedload(Alert.instrument))

    return (await db.execute(query)).scalars().all()


async def create_alert(db: DB, ticker: str, external_id: str, price: Decimal) -> Alert:
    instrument = await instrument_services.get_saved_instrument(db, ticker)

    alert = Alert(instrument_id=instrument.id, external_id=external_id, price=price)
    db.add(alert)
    await db.commit()

    return alert


async def get_alert(db: DB, **kwargs) -> Alert:
    result = await db.execute(select(Alert).filter_by(**kwargs))

    return result.unique().scalar_one()


async def update_alert(db: DB, external_id: str, price: Decimal) -> Alert:
    alert = await get_alert(db, external_id=external_id)
    alert.price = price
    await db.commit()

    return alert


async def delete_alert(db: DB, external_id: str) -> None:
    alert = await get_alert(db, external_id=external_id)

    await db.delete(alert)
    await db.commit()
