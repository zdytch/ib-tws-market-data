from config.db import Base
from common.models import BaseMixin
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime


class Indicator(Base, BaseMixin):
    bar_set_id = Column(ForeignKey('barset.id'))
    length = Column(Integer(), nullable=False)
    atr = Column(Numeric(), nullable=False)
    valid_until = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    bar_set = relationship('BarSet', backref='indicators')

    __table_args__ = (UniqueConstraint('bar_set_id', 'length'),)
