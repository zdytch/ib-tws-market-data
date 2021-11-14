from pydantic import BaseModel
from instruments.models import Exchange, InstrumentType
from common.schemas import Interval
from decimal import Decimal


class InstrumentInfo(BaseModel):
    symbol: str
    ib_symbol: str
    exchange: Exchange
    type: InstrumentType
    description: str
    tick_size: Decimal
    multiplier: Decimal
    nearest_session: Interval
