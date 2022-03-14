from pydantic import BaseModel
from datetime import datetime


class Interval(BaseModel):
    start: datetime
    end: datetime
