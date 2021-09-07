from bars.models import BarLot, Bar, Range
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

        await _perform_range_defragmentation()


async def get_bars(bar_lot: BarLot, range: Range) -> list[Bar]:
    return await Bar.objects.filter(
        bar_lot=bar_lot, t__gte=range.from_t, t__lte=range.to_t
    ).all()


async def _perform_range_defragmentation() -> None:
    pass
    # in_progress = True
    # while in_progress:
    #     try:
    #         ranges = [Range(**dic) for dic in await collection.find().to_list(999)]

    #         for range in ranges:
    #             for compare_range in ranges:
    #                 if compare_range is not range and (
    #                     range.from_t <= compare_range.from_t <= range.to_t
    #                     or range.from_t <= compare_range.to_t <= range.to_t
    #                 ):
    #                     min_t = min((compare_range.from_t, range.from_t))
    #                     max_t = max((compare_range.to_t, range.to_t))

    #                     # TODO: Delete by id
    #                     await collection.delete_many(
    #                         {'from_t': {'$in': [compare_range.from_t, range.from_t]}}
    #                     )
    #                     await collection.insert_one({'from_t': min_t, 'to_t': max_t})

    #                     raise StopIteration

    #         in_progress = False

    #     except StopIteration:
    #         pass
