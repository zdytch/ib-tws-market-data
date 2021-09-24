from bars.models import BarSet, Bar, BarRange
from common.schemas import Range
from asyncpg.exceptions import UniqueViolationError
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
    ranges_to_delete = []

    for range_a in ranges:
        for range_b in ranges:
            if (
                range_a is not range_b
                and range_a not in ranges_to_delete
                and range_b not in ranges_to_delete
                and (
                    range_a.from_dt - step_size
                    <= range_b.from_dt
                    <= range_a.to_dt + step_size
                    or range_a.from_dt - step_size
                    <= range_b.to_dt
                    <= range_a.to_dt + step_size
                )
            ):
                range_a.from_dt = min(range_a.from_dt, range_b.from_dt)
                range_a.to_dt = max(range_a.to_dt, range_b.to_dt)
                ranges_to_delete.append(range_b)

    if ranges_to_delete:
        async with BarRange.Meta.database.transaction():
            for range in ranges:
                if range in ranges_to_delete:
                    await range.delete()
                else:
                    await range.update(['from_dt', 'to_dt'])
