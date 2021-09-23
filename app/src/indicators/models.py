import ormar
from config.db import BaseMeta
from bars.models import BarSet
from decimal import Decimal
from datetime import datetime


class Indicator(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    bar_set: BarSet = ormar.ForeignKey(BarSet, skip_reverse=True, ondelete='CASCADE')
    length: int = ormar.Integer(minimum=1)  # type: ignore
    atr: Decimal = ormar.Decimal(max_digits=12, decimal_places=4, minimum=0.0, default=0.0)  # type: ignore
    valid_until: datetime = ormar.DateTime(default=datetime.now, timezone=True)  # type: ignore

    class Meta(BaseMeta):
        constraints = [ormar.UniqueColumns('bar_set', 'length')]
