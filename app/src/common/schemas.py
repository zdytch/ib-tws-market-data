from pydantic import BaseModel
from datetime import datetime


class Range(BaseModel):
    from_t: int
    to_t: int

    def __str__(self):
        return (
            f'from_t={self.from_t}({datetime.fromtimestamp(self.from_t)}) '
            f'to_t={self.to_t}({datetime.fromtimestamp(self.to_t)})'
        )
