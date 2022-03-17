from pydantic import BaseModel
from decimal import Decimal


class History(BaseModel):
    o: list[Decimal] = []
    h: list[Decimal] = []
    l: list[Decimal] = []
    c: list[Decimal] = []
    v: list[int] = []
    t: list[int] = []
    s: str = 'no_data'
    nextTime: int | None = None


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


class SearchResult(BaseModel):
    symbol: str
    full_name: str
    ticker: str
    description: str
    exchange: str
    type: str


class Config(BaseModel):
    supported_resolutions: list[str]
    supports_search: bool
    supports_group_request: bool
    supports_marks: bool
    supports_timescale_marks: bool
