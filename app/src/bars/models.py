from common.models import Base
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


class BarSet(Base):
    instrument_id = Column(ForeignKey('instrument.id'))
    timeframe = Column(EnumField(Timeframe), nullable=False)

    instrument = relationship('Instrument', back_populates='bar_sets')


class Bar(Base):
    bar_set_id = Column(ForeignKey('barset.id'))
    open = Column(Numeric(), nullable=False)
    high = Column(Numeric(), nullable=False)
    low = Column(Numeric(), nullable=False)
    close = Column(Numeric(), nullable=False)
    volume = Column(Integer(), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    bar_set = relationship('BarSet', back_populates='bars')

    __table_args__ = UniqueConstraint('bar_set_id', 'timestamp')
    __mapper_args__ = {'order_by': timestamp}


class BarRange(Base):
    bar_set_id = Column(ForeignKey('barset.id'))
    from_dt = Column(DateTime(timezone=True), nullable=False)
    to_dt = Column(DateTime(timezone=True), nullable=False)

    bar_set = relationship('BarSet', back_populates='bar_ranges')

    __mapper_args__ = {'order_by': from_dt}
