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


class BarSet(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    instrument: Instrument = ormar.ForeignKey(
        Instrument, skip_reverse=True, ondelete='CASCADE'
    )
    timeframe: Timeframe = ormar.String(max_length=3, choices=list(Timeframe))  # type: ignore

    class Meta(BaseMeta):
        pass


class Bar(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    bar_set: BarSet = ormar.ForeignKey(BarSet, related_name='bars', ondelete='CASCADE')
    open: Decimal = ormar.Decimal(max_digits=18, decimal_places=8)  # type: ignore
    high: Decimal = ormar.Decimal(max_digits=18, decimal_places=8)  # type: ignore
    low: Decimal = ormar.Decimal(max_digits=18, decimal_places=8)  # type: ignore
    close: Decimal = ormar.Decimal(max_digits=18, decimal_places=8)  # type: ignore
    volume: int = ormar.Integer(minimum=0, default=0)  # type: ignore
    timestamp: datetime = ormar.DateTime(timezone=True)  # type: ignore

    class Meta(BaseMeta):
        constraints = [ormar.UniqueColumns('bar_set', 'timestamp')]
        orders_by = ['timestamp']


class BarRange(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    bar_set: BarSet = ormar.ForeignKey(
        BarSet, related_name='ranges', ondelete='CASCADE'
    )
    from_t: int = ormar.Integer(minimum=0, default=0)  # type: ignore
    to_t: int = ormar.Integer(minimum=0, default=0)  # type: ignore

    class Meta(BaseMeta):
        orders_by = ['from_t']

    def __str__(self):
        return (
            f'from_t={self.from_t}({datetime.fromtimestamp(self.from_t)}) '
            f'to_t={self.to_t}({datetime.fromtimestamp(self.to_t)})'
        )

    def __repr__(self):
        return self.__str__()
