from common.repositories import BaseRepository
from .models import Bar, BarSet, BarRange

bar_repo = BaseRepository(Bar)
bar_set_repo = BaseRepository(BarSet)
bar_range_repo = BaseRepository(BarRange)
