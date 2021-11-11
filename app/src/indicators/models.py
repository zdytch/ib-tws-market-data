from common.models import DBModel
from sqlmodel import Field, Column, DateTime, ForeignKey, Relationship
from sqlalchemy import UniqueConstraint, orm
from bars.models import BarSet
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class Indicator(DBModel, table=True):
    bar_set_id: UUID = Field(
        sa_column=Column(ForeignKey('barset.id', ondelete='CASCADE'), nullable=False)
    )
    bar_set: BarSet = Relationship(
        sa_relationship=orm.RelationshipProperty('BarSet', backref='indicators')
    )
    length: int
    atr: Decimal
    valid_until: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    )

    __table_args__ = (UniqueConstraint('bar_set_id', 'length'),)
