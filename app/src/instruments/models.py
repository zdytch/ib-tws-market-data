# TODO: Remove workaround
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
    String,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
import enum
from datetime import datetime


class Exchange(enum.Enum):
    NYSE = 'NYSE'
    NASDAQ = 'NASDAQ'
    GLOBEX = 'GLOBEX'
    NYMEX = 'NYMEX'
    ECBOT = 'ECBOT'


class InstrumentType(enum.Enum):
    STOCK = 'STK'
    FUTURE = 'FUT'


class Instrument(BaseModel):
    symbol = Column(String(8), nullable=False)
    ib_symbol = Column(String(8), nullable=False)
    exchange = Column(Enum(Exchange), nullable=False)
    type = Column(Enum(InstrumentType), nullable=False)
    description = Column(String(64), nullable=False)
    tick_size = Column(Numeric(), nullable=False)
    multiplier = Column(Numeric(), nullable=False)

    __table_args__ = (UniqueConstraint('symbol', 'exchange'),)


class TradingSession(BaseModel):
    instrument_id = Column(ForeignKey('instrument.id', ondelete='CASCADE'))
    open_dt = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    close_dt = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    instrument = relationship('Instrument', backref='sessions')
