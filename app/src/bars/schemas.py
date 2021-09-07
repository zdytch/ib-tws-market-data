from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from instruments.schemas import Instrument


class Timeframe(str, Enum):
    M1 = '1'
    M5 = '5'
    M15 = '15'
    M30 = '30'
    M60 = '60'
    DAY = 'D'
    WEEK = 'W'
    MONTH = 'M'


class Bar(BaseModel):
    o: float
    h: float
    l: float
    c: float
    v: int
    t: int

    def __str__(self):
        return (
            f'o={self.o} h={self.h} l={self.l} c={self.c} v={self.v} '
            f't={self.t}({datetime.fromtimestamp(self.t)})'
        )


class BarList(BaseModel):
    instrument: Instrument
    timeframe: Timeframe
    bars: list[Bar]


class Range(BaseModel):
    from_t: int
    to_t: int

    def __str__(self):
        return (
            f'from_t={self.from_t}({datetime.fromtimestamp(self.from_t)}) '
            f'to_t={self.to_t}({datetime.fromtimestamp(self.to_t)})'
        )
