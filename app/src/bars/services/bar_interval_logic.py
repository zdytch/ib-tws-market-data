from bars.models import BarSet, BarInterval, Timeframe
from common.schemas import Interval
from config.db import DB
from sqlalchemy.future import select
from datetime import timedelta
import math


async def perform_defragmentation(db: DB, bar_set: BarSet) -> None:
    step_size = _get_step_size(bar_set.timeframe)
    intervals_to_delete = []

    intervals = (
        (await db.execute(select(BarInterval).where(BarInterval.bar_set == bar_set)))
        .scalars()
        .all()
    )

    for interval_a in intervals:
        for interval_b in intervals:
            if (
                interval_a is not interval_b
                and interval_a not in intervals_to_delete
                and interval_b not in intervals_to_delete
                and (
                    interval_a.start - step_size
                    <= interval_b.start
                    <= interval_a.end + step_size
                    or interval_a.start - step_size
                    <= interval_b.end
                    <= interval_a.end + step_size
                )
            ):
                interval_a.start = min(interval_a.start, interval_b.start)
                interval_a.end = max(interval_a.end, interval_b.end)
                intervals_to_delete.append(interval_b)

    for interval in intervals_to_delete:
        await db.delete(interval)


def split_intervals(
    intervals: list[Interval], timeframe: Timeframe, length: int
) -> list[Interval]:
    splitted_intervals = []
    step_size = _get_step_size(timeframe)

    for interval_to_split in intervals:
        bar_count = math.ceil(
            (interval_to_split.end - interval_to_split.start) / step_size
        )
        part_count = math.ceil(bar_count / length)

        end = interval_to_split.end
        for _ in range(part_count):
            start = end - length * step_size
            if start < interval_to_split.start:
                start = interval_to_split.start

            splitted_interval = Interval(start=start, end=end)
            splitted_intervals.append(splitted_interval)
            end = start - step_size

    return splitted_intervals


def calculate_missing_intervals(
    within_interval: Interval, existing_intervals: list[BarInterval]
) -> list[Interval]:
    missing_intervals = []
    next_start = within_interval.start

    for interval in existing_intervals:
        if (
            interval.end > within_interval.start
            and interval.start < within_interval.end
        ):
            if interval.start > next_start < within_interval.end:
                missing_intervals.append(Interval(start=next_start, end=interval.start))

            next_start = interval.end

    if next_start < within_interval.end:
        missing_intervals.append(Interval(start=next_start, end=within_interval.end))

    return missing_intervals


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
