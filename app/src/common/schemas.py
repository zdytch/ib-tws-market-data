from pydantic import BaseModel
from datetime import datetime


class Range(BaseModel):
    from_dt: datetime
    to_dt: datetime
