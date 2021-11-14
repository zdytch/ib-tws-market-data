from common.models import DBModel
from sqlmodel import Field, Column, Enum, DateTime, ForeignKey, Relationship
from sqlalchemy import UniqueConstraint
from uuid import UUID
from decimal import Decimal
from datetime import datetime
import enum
import pytz


class Exchange(enum.Enum):
    NYSE = 'NYSE'
    NASDAQ = 'NASDAQ'
    GLOBEX = 'GLOBEX'
    NYMEX = 'NYMEX'
    ECBOT = 'ECBOT'


class InstrumentType(enum.Enum):
    STOCK = 'STK'
    FUTURE = 'FUT'


class Instrument(DBModel, table=True):
    symbol: str
    ib_symbol: str
    exchange: Exchange = Field(sa_column=Column(Enum(Exchange), nullable=False))
    type: InstrumentType = Field(sa_column=Column(Enum(InstrumentType), nullable=False))
    description: str
    tick_size: Decimal
    multiplier: Decimal

    __table_args__ = (UniqueConstraint('symbol', 'exchange'),)


class TradingSession(DBModel, table=True):
    instrument_id: UUID = Field(
        sa_column=Column(
            ForeignKey('instrument.id', ondelete='CASCADE'), nullable=False
        )
    )
    instrument: Instrument = Relationship()
    open_dt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: pytz.utc.localize(datetime.min),
    )
    close_dt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: pytz.utc.localize(datetime.min),
    )
