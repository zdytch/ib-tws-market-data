from pydantic import BaseModel, Field
from typing import Optional


class History(BaseModel):
    o: list[float] = []
    h: list[float] = []
    l: list[float] = []
    c: list[float] = []
    v: list[int] = []
    t: list[int] = []
    s: str = 'no_data'
    next_time: Optional[int] = Field(alias='nextTime')

    class Config:
        allow_population_by_field_name = True


class Info(BaseModel):
    name: str
    ticker: str
    type: str
    description: str
    exchange: str
    listed_exchange: str
    session: str
    timezone: str
    currency_code: str
    has_daily: str
    has_intraday: str
    minmov: int
    pricescale: int


class Config(BaseModel):
    supported_resolutions: list[str]
    supports_search: bool
    supports_group_request: bool
    supports_marks: bool
    supports_timescale_marks: bool
