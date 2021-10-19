from pydantic import BaseModel
from .models import InstrumentType
from datetime import datetime
from decimal import Decimal


class InstrumentGet(BaseModel):
    symbol: str
    exchange: str
    type: InstrumentType
    description: str
    tick_size: Decimal
    multiplier: Decimal
    sector: str | None
    industry: str | None


class InstrumentList(InstrumentGet):
    pass


class SessionGet(BaseModel):
    open_dt: datetime
    close_dt: datetime
