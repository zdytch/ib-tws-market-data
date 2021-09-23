from pydantic import BaseModel
from bars.models import Timeframe
from datetime import datetime
from decimal import Decimal


class IndicatorGet(BaseModel):
    length: int
    atr: Decimal
    valid_until: datetime
