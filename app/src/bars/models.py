from common.models import DBModel
from sqlmodel import Field, Column, Enum, DateTime, ForeignKey, Relationship
from sqlalchemy import UniqueConstraint, orm
from instruments.models import Instrument
from uuid import UUID
from decimal import Decimal
from datetime import datetime
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


class BarSet(DBModel, table=True):
    instrument_id: UUID = Field(
        sa_column=Column(
            ForeignKey('instrument.id', ondelete='CASCADE'), nullable=False
        )
    )
    instrument: Instrument = Relationship(
        sa_relationship=orm.RelationshipProperty('Instrument', backref='bar_sets')
    )
    timeframe: Timeframe = Field(sa_column=Column(Enum(Timeframe)))


class Bar(DBModel, table=True):
    bar_set_id: UUID = Field(
        sa_column=Column(ForeignKey('barset.id', ondelete='CASCADE'), nullable=False)
    )
    bar_set: BarSet = Relationship(
        sa_relationship=orm.RelationshipProperty('BarSet', backref='bars')
    )
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    __table_args__ = (UniqueConstraint('bar_set_id', 'timestamp'),)


class BarRange(DBModel, table=True):
    bar_set_id: UUID = Field(
        sa_column=Column(ForeignKey('barset.id', ondelete='CASCADE'), nullable=False)
    )
    bar_set: BarSet = Relationship(
        sa_relationship=orm.RelationshipProperty('BarSet', backref='bar_ranges')
    )
    from_dt: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    to_dt: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
