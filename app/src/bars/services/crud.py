from bars.models import BarSet, Bar, BarRange
from common.schemas import Range
from asyncpg.exceptions import UniqueViolationError
from datetime import datetime
from . import utils


async def add_bars(bar_set: BarSet, bars: list[Bar]) -> None:
    if bars:
        # TODO: Ormar's bulk_create() seems to work incorrectly. Implement with SQLAlchemy 2.0
        for bar in bars:
            try:
                await bar.save()
            except UniqueViolationError:
                pass

        min_dt = min(bars, key=lambda bar: bar.timestamp).timestamp
        max_dt = max(bars, key=lambda bar: bar.timestamp).timestamp

        await BarRange.objects.create(bar_set=bar_set, from_dt=min_dt, to_dt=max_dt)

        await _perform_range_defragmentation(bar_set)


async def get_bars(bar_set: BarSet, range: Range) -> list[Bar]:
    return await Bar.objects.filter(
        bar_set=bar_set, timestamp__gte=range.from_dt, timestamp__lte=range.to_dt
    ).all()


async def _perform_range_defragmentation(bar_set: BarSet) -> None:
    ranges = await BarRange.objects.filter(bar_set=bar_set).all()
    step_size = utils.get_step_size(bar_set.timeframe)

    is_updated = False
    for range in ranges:
        for next_range in ranges:
            if (
                range.from_dt
                and range.to_dt
                and next_range.from_dt
                and next_range.to_dt
                and next_range is not range
                and (
                    range.from_dt - step_size
                    <= next_range.from_dt
                    <= range.to_dt + step_size
                    or range.from_dt - step_size
                    <= next_range.to_dt
                    <= range.to_dt + step_size
                )
            ):
                range.from_dt = min((next_range.from_dt, range.from_dt))
                range.to_dt = max((next_range.to_dt, range.to_dt))
                next_range.from_dt = datetime.min
                next_range.to_dt = datetime.min
                is_updated = True

    if is_updated:
        async with BarRange.Meta.database.transaction():
            for range in ranges:
                if range.from_dt and range.to_dt:
                    await range.update(['from_dt', 'to_dt'])
                else:
                    await range.delete()
