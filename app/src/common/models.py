from typing import Optional
from sqlmodel import SQLModel, Field


class Model(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
