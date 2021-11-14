from bars.models import BarSet, BarRange, Timeframe
from common.schemas import Range
from config.db import DB
from sqlalchemy.future import select
from datetime import timedelta
import math


async def perform_defragmentation(db: DB, bar_set: BarSet) -> None:
    step_size = _get_step_size(bar_set.timeframe)
    ranges_to_delete = []

    ranges = (
        (await db.execute(select(BarRange).where(BarRange.bar_set == bar_set)))
        .scalars()
        .all()
    )

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

    for range in ranges_to_delete:
        await db.delete(range)


def split_ranges(ranges: list[Range], timeframe: Timeframe, length: int) -> list[Range]:
    splitted_ranges = []
    step_size = _get_step_size(timeframe)

    for range_to_split in ranges:
        bar_count = math.ceil(
            (range_to_split.to_dt - range_to_split.from_dt) / step_size
        )
        part_count = math.ceil(bar_count / length)

        to_dt = range_to_split.to_dt
        for _ in range(part_count):
            from_dt = to_dt - length * step_size
            if from_dt < range_to_split.from_dt:
                from_dt = range_to_split.from_dt

            splitted_range = Range(from_dt=from_dt, to_dt=to_dt)
            splitted_ranges.append(splitted_range)
            to_dt = from_dt - step_size

    return splitted_ranges


def calculate_missing_ranges(
    within_range: Range, existing_ranges: list[BarRange]
) -> list[Range]:
    missing_ranges = []
    next_from_dt = within_range.from_dt

    for range in existing_ranges:
        if range.to_dt > within_range.from_dt and range.from_dt < within_range.to_dt:
            if range.from_dt > next_from_dt < within_range.to_dt:
                missing_ranges.append(Range(from_dt=next_from_dt, to_dt=range.from_dt))

            next_from_dt = range.to_dt

    if next_from_dt < within_range.to_dt:
        missing_ranges.append(Range(from_dt=next_from_dt, to_dt=within_range.to_dt))

    return missing_ranges


def _get_step_size(timeframe: Timeframe) -> timedelta:
    if timeframe == Timeframe.M1:
        step_size = timedelta(minutes=1)
    elif timeframe == Timeframe.M5:
        step_size = timedelta(minutes=5)
    elif timeframe == Timeframe.M30:
        step_size = timedelta(minutes=30)
    elif timeframe == Timeframe.M60:
        step_size = timedelta(hours=1)
    elif timeframe == Timeframe.DAY:
        step_size = timedelta(days=1)
    elif timeframe == Timeframe.WEEK:
        step_size = timedelta(days=7)
    elif timeframe == Timeframe.MONTH:
        step_size = timedelta(days=30)  # TODO: Better approach
    else:
        raise ValueError(f'Cannot get step size for timeframe {timeframe}')

    return step_size
