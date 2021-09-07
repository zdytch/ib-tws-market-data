from pydantic import BaseModel
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


class TradingSession(BaseModel):
    open_t: int
    close_t: int

    def __str__(self):
        return (
            f'open_t={self.open_t}({datetime.fromtimestamp(self.open_t)}) '
            f'close_t={self.close_t}({datetime.fromtimestamp(self.close_t)})'
        )


class Instrument(BaseModel):
    symbol: str
    exchange: Exchange
    type: InstrumentType
    description: str
    tick_size: Decimal
    multiplier: Decimal
    nearest_session: TradingSession

    def __str__(self):
        return (
            f'symbol={self.symbol} exchange={self.exchange} type={self.type} '
            f'description={self.description} tick_size={self.tick_size} multiplier={self.multiplier} '
            f'nearest_session={self.nearest_session}'
        )
