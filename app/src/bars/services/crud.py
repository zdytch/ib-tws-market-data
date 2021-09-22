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

        min_t = min(bars, key=lambda bar: bar.t).t
        max_t = max(bars, key=lambda bar: bar.t).t

        await BarRange.objects.create(bar_set=bar_set, from_t=min_t, to_t=max_t)

        await _perform_range_defragmentation(bar_set)


async def get_bars(bar_set: BarSet, range: Range) -> list[Bar]:
    return await Bar.objects.filter(
        bar_set=bar_set, t__gte=range.from_t, t__lte=range.to_t
    ).all()


async def _perform_range_defragmentation(bar_set: BarSet) -> None:
    ranges = await BarRange.objects.filter(bar_set=bar_set).all()
    step_size = utils.get_step_size(bar_set.timeframe)

    is_updated = False
    for range in ranges:
        for next_range in ranges:
            if (
                range.from_t
                and range.to_t
                and next_range.from_t
                and next_range.to_t
                and next_range is not range
                and (
                    range.from_t - step_size
                    <= next_range.from_t
                    <= range.to_t + step_size
                    or range.from_t - step_size
                    <= next_range.to_t
                    <= range.to_t + step_size
                )
            ):
                range.from_t = min((next_range.from_t, range.from_t))
                range.to_t = max((next_range.to_t, range.to_t))
                next_range.from_t = 0
                next_range.to_t = 0
                is_updated = True

    if is_updated:
        async with BarRange.Meta.database.transaction():
            for range in ranges:
                if range.from_t and range.to_t:
                    await range.update(['from_t', 'to_t'])
                else:
                    await range.delete()
