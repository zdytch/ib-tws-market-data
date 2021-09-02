from pydantic import BaseModel
from decimal import Decimal


class Bar(BaseModel):
    o: Decimal
    h: Decimal
    l: Decimal
    c: Decimal
    v: int
    t: int
