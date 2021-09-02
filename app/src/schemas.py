from pydantic import BaseModel
from decimal import Decimal
from enum import Enum


class Timeframe(str, Enum):
    M1 = '1'
    M5 = '5'
    M15 = '15'
    M30 = '30'
    M60 = '60'
    DAY = '1D'
    WEEK = '1W'
    MONTH = '1M'


class InstrumentType(str, Enum):
    STOCK = 'STK'
    FUTURE = 'FUT'


class Bar(BaseModel):
    o: Decimal
    h: Decimal
    l: Decimal
    c: Decimal
    v: int
    t: int
