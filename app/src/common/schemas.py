from pydantic import BaseModel


class Range(BaseModel):
    from_t: int
    to_t: int
