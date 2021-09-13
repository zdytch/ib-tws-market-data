from typing import Optional
from pydantic import BaseModel
from .models import InstrumentType
from decimal import Decimal


class InstrumentGet(BaseModel):
    symbol: str
    exchange: str
    type: InstrumentType
    description: str
    tick_size: Decimal
    multiplier: Decimal
    sector: Optional[str]
    industry: Optional[str]


class InstrumentList(InstrumentGet):
    pass
