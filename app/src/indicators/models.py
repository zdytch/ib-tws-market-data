from common.models import IDMixin
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, orm
from bars.models import BarSet
from decimal import Decimal
from datetime import datetime


class Indicator(SQLModel, IDMixin, table=True):
    bar_set_id: int = Field(foreign_key='barset.id')
    length: int
    atr: Decimal
    valid_until: datetime = Field(default=datetime.now)

    bar_set: BarSet = Relationship(
        sa_relationship=orm.RelationshipProperty('BarSet', backref='indicators')
    )

    __table_args__ = (UniqueConstraint('bar_set_id', 'length'),)
