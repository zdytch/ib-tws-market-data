from pydantic import BaseModel, Field
from typing import Optional


class ChartData(BaseModel):
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
