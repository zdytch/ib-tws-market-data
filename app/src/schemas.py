from pydantic import BaseModel
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


class Exchange(str, Enum):
    NYSE = 'NYSE'
    NASDAQ = 'NASDAQ'
    GLOBEX = 'GLOBEX'
    NYMEX = 'NYMEX'
    ECBOT = 'ECBOT'


class Bar(BaseModel):
    o: float
    h: float
    l: float
    c: float
    v: int
    t: int


class ChartData(BaseModel):
    o: list[float] = []
    h: list[float] = []
    l: list[float] = []
    c: list[float] = []
    v: list[int] = []
    t: list[int] = []
    s: str = 'no_data'
