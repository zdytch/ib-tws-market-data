from common.models import IDMixin
from sqlmodel import SQLModel, Field, Column, Enum, DateTime, ForeignKey, Relationship
from sqlalchemy import UniqueConstraint, orm
from decimal import Decimal
from datetime import datetime
import enum


class Exchange(enum.Enum):
    NYSE = 'NYSE'
    NASDAQ = 'NASDAQ'
    GLOBEX = 'GLOBEX'
    NYMEX = 'NYMEX'
    ECBOT = 'ECBOT'


class InstrumentType(enum.Enum):
    STOCK = 'STK'
    FUTURE = 'FUT'


class Instrument(SQLModel, IDMixin, table=True):
    symbol: str
    ib_symbol: str
    exchange: Exchange = Field(sa_column=Column(Enum(Exchange), nullable=False))
    type: InstrumentType = Field(sa_column=Column(Enum(InstrumentType), nullable=False))
    description: str
    tick_size: Decimal
    multiplier: Decimal

    __table_args__ = (UniqueConstraint('symbol', 'exchange'),)


class TradingSession(SQLModel, IDMixin, table=True):
    instrument_id: int = Field(
        sa_column=Column(
            ForeignKey('instrument.id', ondelete='CASCADE'), nullable=False
        )
    )
    instrument: Instrument = Relationship(
        sa_relationship=orm.RelationshipProperty(
            'Instrument', backref='session', uselist=False
        )
    )
    open_dt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    )
    close_dt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    )
