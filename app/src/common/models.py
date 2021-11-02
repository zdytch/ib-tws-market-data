from config.db import Base
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def instance_values(self) -> dict:
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith('_')
        }

    def db_values(self) -> dict:
        db_values = {}

        for key, value in self.instance_values().items():
            if not isinstance(value, BaseModel):
                db_values[key] = value
            else:
                db_values[f'{key}_id'] = value.id

        return db_values

    def __repr__(self) -> str:
        attr_repr = ''

        for attr, value in sorted(self.instance_values().items()):
            if attr != 'id':
                attr_repr += f', {attr}={repr(value)}'

        return f'{self.__class__.__name__}(id={self.id}{attr_repr})'
