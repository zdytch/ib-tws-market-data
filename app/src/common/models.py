from config.db import Base
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def dict(self) -> dict:
        return {
            key: value
            for (key, value) in self.__dict__.items()
            if not key.startswith('_')
        }

    def __repr__(self) -> str:
        fields = sorted(self.dict().items())
        all_attr_string = ''

        for attr, value in fields:
            if attr != 'id':
                all_attr_string += f', {attr}={repr(value)}'

        return f'{self.__class__.__name__}(id={self.id}{all_attr_string})'
