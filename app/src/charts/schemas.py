from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class History(BaseModel):
    o: list[Decimal] = []
    h: list[Decimal] = []
    l: list[Decimal] = []
    c: list[Decimal] = []
    v: list[int] = []
    t: list[int] = []
    s: str = 'no_data'
    nextTime: Optional[int]


class Info(BaseModel):
    name: str
    ticker: str
    type: str = ''
    description: str = ''
    exchange: str = ''
    listed_exchange: str = ''
    session: str = '24x7'
    timezone: str = ''
    currency_code: str = 'USD'
    has_daily: bool = True
    has_intraday: bool = True
    minmov: int = 0
    pricescale: int = 0


class Config(BaseModel):
    supported_resolutions: list[str]
    supports_search: bool
    supports_group_request: bool
    supports_marks: bool
    supports_timescale_marks: bool
