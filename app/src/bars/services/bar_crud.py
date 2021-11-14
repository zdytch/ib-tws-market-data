from bars.models import BarSet, Bar, BarInterval
from common.schemas import Interval
from config.db import DB
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from datetime import datetime
import pytz
from . import bar_interval_logic


async def get_bars(db: DB, bar_set: BarSet, interval: Interval) -> list[Bar]:
    result = await db.execute(
        select(Bar)
        .where(Bar.bar_set == bar_set)
        .where(Bar.timestamp >= interval.start)
        .where(Bar.timestamp <= interval.end)
        .order_by(Bar.timestamp)
    )

    return result.scalars().all()


async def get_latest_timestamp(db: DB, bar_set: BarSet) -> datetime:
    latest_ts = (
        await db.execute(select(func.max(Bar.timestamp)).filter_by(bar_set=bar_set))
    ).scalar()

    return latest_ts or pytz.utc.localize(datetime.min)


async def bulk_save_bars(db: DB, bar_set: BarSet, bars: list[Bar]) -> None:
    if bars:
        min_ts = min(bars, key=lambda bar: bar.timestamp).timestamp
        max_ts = max(bars, key=lambda bar: bar.timestamp).timestamp
        bar_values = [bar.dict(exclude_none=True) for bar in bars]
        bar_interval = BarInterval(bar_set_id=bar_set.id, start=min_ts, end=max_ts)

        await db.execute(insert(Bar).values(bar_values).on_conflict_do_nothing())

        db.add(bar_interval)

        await bar_interval_logic.perform_defragmentation(db, bar_set)

        await db.commit()
