# Workaround for SQLAlchemy Enum typing:
# https://github.com/dropbox/sqlalchemy-stubs/issues/114
from typing import TypeVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.sql.type_api import TypeEngine

    T = TypeVar('T')

    class Enum(TypeEngine[T]):
        def __init__(self, enum: Type[T]) -> None:
            ...


else:
    from sqlalchemy import Enum
# End

from common.models import BaseModel
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
import enum


class Timeframe(enum.Enum):
    M1 = '1'
    M5 = '5'
    M15 = '15'
    M30 = '30'
    M60 = '60'
    DAY = 'D'
    WEEK = 'W'
    MONTH = 'M'


class BarSet(BaseModel):
    instrument_id = Column(ForeignKey('instrument.id'))
    timeframe = Column(Enum(Timeframe), nullable=False)

    instrument = relationship('Instrument', backref='bar_sets')


class Bar(BaseModel):
    bar_set_id = Column(ForeignKey('barset.id'))
    open = Column(Numeric(), nullable=False)
    high = Column(Numeric(), nullable=False)
    low = Column(Numeric(), nullable=False)
    close = Column(Numeric(), nullable=False)
    volume = Column(Integer(), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    bar_set = relationship('BarSet', backref='bars')

    __table_args__ = (UniqueConstraint('bar_set_id', 'timestamp'),)


class BarRange(BaseModel):
    bar_set_id = Column(ForeignKey('barset.id'))
    from_dt = Column(DateTime(timezone=True), nullable=False)
    to_dt = Column(DateTime(timezone=True), nullable=False)

    bar_set = relationship('BarSet', backref='bar_ranges')
