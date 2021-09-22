from decimal import Decimal, ROUND_HALF_UP


def round_with_quantum(number: Decimal, quantum: Decimal) -> Decimal:
    return quantum * (number / quantum).quantize(Decimal('1.'), ROUND_HALF_UP)
