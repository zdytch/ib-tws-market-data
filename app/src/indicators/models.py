from common.models import Base
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


class Indicator(Base):
    bar_set_id = Column(ForeignKey('barset.id'))
    length = Column(Integer(), nullable=False)
    atr = Column(Numeric(), nullable=False)
    valid_until = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    bar_set = relationship('BarSet', back_populates='indicators')

    __table_args__ = UniqueConstraint('bar_set_id', 'length')
