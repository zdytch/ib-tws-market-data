from pydantic import BaseModel
from instruments.models import Exchange, InstrumentType
from common.schemas import Range
from decimal import Decimal


class InstrumentInfo(BaseModel):
    symbol: str
    exchange: Exchange
    type: InstrumentType
    description: str
    tick_size: Decimal
    multiplier: Decimal
    trading_session: Range
