from common.models import BaseModel
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    Enum as EnumField,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from enum import Enum


class Timeframe(str, Enum):
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
    timeframe = Column(EnumField(Timeframe), nullable=False)

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
