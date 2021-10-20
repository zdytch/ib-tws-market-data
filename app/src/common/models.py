from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr


class BaseMixin:
    id = Column(Integer, primary_key=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
