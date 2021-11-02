from bars.models import BarSet, Bar
from bars.repositories import bar_repo, bar_range_repo
from common.schemas import Range
from . import utils


async def add_bars(bar_set: BarSet, bars: list[Bar]) -> None:
    if bars:
        await bar_repo.bulk_save(bars)

        min_dt = min(bars, key=lambda bar: bar.timestamp).timestamp
        max_dt = max(bars, key=lambda bar: bar.timestamp).timestamp

        await bar_range_repo.create(bar_set=bar_set, from_dt=min_dt, to_dt=max_dt)

        await _perform_range_defragmentation(bar_set)


async def get_bars(bar_set: BarSet, range: Range) -> list[Bar]:
    return await bar_repo.get_bars_in_range(bar_set, range)


async def _perform_range_defragmentation(bar_set: BarSet) -> None:
    ranges = await bar_range_repo.filter(bar_set=bar_set)
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
        # TODO: Business transaction
        for range in ranges:
            if range in ranges_to_delete:
                await bar_range_repo.delete(range)
            else:
                await bar_range_repo.update(range)
