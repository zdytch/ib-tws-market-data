from types import SimpleNamespace
from config.db import Base
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr


class BaseModel(Base, SimpleNamespace):
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
