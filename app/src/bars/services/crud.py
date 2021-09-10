from bars.models import BarLot, Bar, Range, Timeframe
from asyncpg.exceptions import UniqueViolationError


async def create_bars(bar_lot: BarLot, bars: list[Bar]) -> None:
    if bars:
        try:
            await Bar.objects.bulk_create(bars)
        except UniqueViolationError:
            pass

        min_t = min(bars, key=lambda bar: bar.t).t
        max_t = max(bars, key=lambda bar: bar.t).t

        await Range.objects.create(bar_lot=bar_lot, from_t=min_t, to_t=max_t)

        await _perform_range_defragmentation(bar_lot)


async def get_bars(bar_lot: BarLot, range: Range) -> list[Bar]:
    return await Bar.objects.filter(
        bar_lot=bar_lot, t__gte=range.from_t, t__lte=range.to_t
    ).all()


async def _perform_range_defragmentation(bar_lot: BarLot) -> None:
    ranges = await Range.objects.filter(bar_lot=bar_lot).all()
    step_size = _get_step_size(bar_lot.timeframe)

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
        async with Range.Meta.database.transaction():
            for range in ranges:
                if range.from_t and range.to_t:
                    await range.update(['from_t', 'to_t'])
                else:
                    await range.delete()


def _get_step_size(timeframe: Timeframe):
    if timeframe == Timeframe.M1:
        step_size = 60
    elif timeframe == Timeframe.M5:
        step_size = 60 * 5
    elif timeframe == Timeframe.M30:
        step_size = 60 * 30
    elif timeframe == Timeframe.M60:
        step_size = 60 * 60
    elif timeframe == Timeframe.DAY:
        step_size = 60 * 60 * 24
    elif timeframe == Timeframe.WEEK:
        step_size = 60 * 60 * 24 * 7
    elif timeframe == Timeframe.MONTH:
        step_size = 60 * 60 * 24 * 7 * 4
    else:
        raise ValueError(f'Cannot get step size for timeframe {timeframe}')

    return step_size
