from typing import Optional
from pydantic import BaseModel
from sqlmodel import Field


class IDMixin(BaseModel):
    id: Optional[int] = Field(default=None, primary_key=True)
