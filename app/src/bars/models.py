from common.models import IDMixin
from sqlmodel import SQLModel, Field, Relationship, Column, Enum
from sqlalchemy import UniqueConstraint, orm
from instruments.models import Instrument
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


class BarSet(SQLModel, IDMixin, table=True):
    instrument_id: int = Field(foreign_key='instrument.id')
    timeframe: Timeframe = Field(sa_column=Column(Enum(Timeframe)))

    instrument: Instrument = Relationship(
        sa_relationship=orm.RelationshipProperty('Instrument', backref='bar_sets')
    )


class Bar(SQLModel, IDMixin, table=True):
    bar_set_id: int = Field(foreign_key='barset.id')
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    timestamp: datetime

    bar_set: BarSet = Relationship(
        sa_relationship=orm.RelationshipProperty('BarSet', backref='bars')
    )

    __table_args__ = (UniqueConstraint('bar_set_id', 'timestamp'),)


class BarRange(SQLModel, IDMixin, table=True):
    bar_set_id: int = Field(foreign_key='barset.id')
    from_dt: datetime
    to_dt: datetime

    bar_set: BarSet = Relationship(
        sa_relationship=orm.RelationshipProperty('BarSet', backref='bar_ranges')
    )
