import ormar
from config.db import BaseMeta
from enum import Enum
from datetime import datetime
from decimal import Decimal


class Exchange(str, Enum):
    NYSE = 'NYSE'
    NASDAQ = 'NASDAQ'
    GLOBEX = 'GLOBEX'
    NYMEX = 'NYMEX'
    ECBOT = 'ECBOT'


class InstrumentType(str, Enum):
    STOCK = 'STK'
    FUTURE = 'FUT'


class Instrument(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    type: InstrumentType = ormar.String(max_length=3, choices=list(InstrumentType))  # type: ignore
    symbol: str = ormar.String(max_length=8)  # type: ignore
    exchange: Exchange = ormar.String(max_length=8, choices=list(Exchange))  # type: ignore
    description: str = ormar.String(max_length=64)  # type: ignore
    tick_size: Decimal = ormar.Decimal(
        max_digits=18, decimal_places=8, minimum=0.0, default=0.0
    )  # type: ignore
    multiplier: Decimal = ormar.Decimal(
        max_digits=12, decimal_places=2, minimum=0.0, default=0.0
    )  # type: ignore

    class Meta(BaseMeta):
        constraints = [ormar.UniqueColumns('symbol', 'exchange')]
        orders_by = ['symbol']


class TradingSession(ormar.Model):
    id: int = ormar.Integer(primary_key=True)  # type: ignore
    instrument: Instrument = ormar.ForeignKey(
        Instrument, related_name='session', unique=True, ondelete='CASCADE'
    )
    open_dt: datetime = ormar.DateTime(timezone=True, default=datetime.now)  # type: ignore
    close_dt: datetime = ormar.DateTime(timezone=True, default=datetime.now)  # type: ignore

    class Meta(BaseMeta):
        pass
