from bars.models import Bar
from common.utils import round_with_quantum
from decimal import Decimal


def _calculate_atr(bars: list[Bar], length: int) -> Decimal:
    atr = Decimal('0.0')

    if 0 < length < len(bars):
        source_bars = sorted(bars, key=lambda bar: bar.t, reverse=True)
        true_ranges = []
        for index, bar in enumerate(source_bars[: length - 1]):
            true_range_option1 = bar.h - bar.l
            true_range_option2 = abs(bar.h - source_bars[index + 1].c)
            true_range_option3 = abs(bar.l - source_bars[index + 1].c)
            true_range = max(true_range_option1, true_range_option2, true_range_option3)
            true_ranges.append(true_range)

        atr = round_with_quantum(
            Decimal(sum(true_ranges) / len(true_ranges)), Decimal('0.0001')
        )

    return atr
