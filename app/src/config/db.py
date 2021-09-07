import sqlalchemy
import databases
import ormar
from .settings import DB_URL

metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DB_URL)
database = databases.Database(DB_URL)


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database
