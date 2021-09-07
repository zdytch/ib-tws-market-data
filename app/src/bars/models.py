import ormar
from config.db import BaseMeta
from instruments.models import Instrument
from enum import Enum
from decimal import Decimal
from datetime import datetime


class Timeframe(str, Enum):
    M1 = '1'
    M5 = '5'
    M15 = '15'
    M30 = '30'
    M60 = '60'
    DAY = 'D'
    WEEK = 'W'
    MONTH = 'M'


class BarLot(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    instrument: Instrument = ormar.ForeignKey(
        Instrument, skip_reverse=True, ondelete='CASCADE'
    )
    timeframe: Timeframe = ormar.String(max_length=3, choices=list(Timeframe))  # type: ignore

    class Meta(BaseMeta):
        pass


class Bar(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    bar_lot: BarLot = ormar.ForeignKey(BarLot, related_name='bars', ondelete='CASCADE')
    o: Decimal = ormar.Decimal(max_digits=18, decimal_places=8)  # type: ignore
    h: Decimal = ormar.Decimal(max_digits=18, decimal_places=8)  # type: ignore
    l: Decimal = ormar.Decimal(max_digits=18, decimal_places=8)  # type: ignore
    c: Decimal = ormar.Decimal(max_digits=18, decimal_places=8)  # type: ignore
    v: int = ormar.Integer(minimum=0, default=0)  # type: ignore
    t: int = ormar.Integer(minimum=0, default=0, unique=True)  # type: ignore

    class Meta(BaseMeta):
        orders_by = ['t']

    def __str__(self):
        return (
            f'o={self.o} h={self.h} l={self.l} c={self.c} v={self.v} '
            f't={self.t}({datetime.fromtimestamp(self.t)})'
        )


class Range(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    bar_lot: BarLot = ormar.ForeignKey(
        BarLot, related_name='ranges', ondelete='CASCADE'
    )
    from_t: int = ormar.Integer(minimum=0, default=0)  # type: ignore
    to_t: int = ormar.Integer(minimum=0, default=0)  # type: ignore

    class Meta(BaseMeta):
        pass

    def __str__(self):
        return (
            f'from_t={self.from_t}({datetime.fromtimestamp(self.from_t)}) '
            f'to_t={self.to_t}({datetime.fromtimestamp(self.to_t)})'
        )
