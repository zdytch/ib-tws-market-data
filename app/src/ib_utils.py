from typing import Union
from ib_insync import BarData
from schemas import Bar, Timeframe
from datetime import datetime, date, time
import math
import pytz


def timeframe_to_ib(timeframe: Timeframe) -> str:
    if timeframe == Timeframe.DAY:
        ib_timeframe = '1 day'
    elif timeframe == Timeframe.M30:
        ib_timeframe = '30 mins'
    elif timeframe == Timeframe.M5:
        ib_timeframe = '5 mins'
    elif timeframe == Timeframe.M1:
        ib_timeframe = '1 min'
    else:
        raise ValueError(f'Cannot convert {timeframe} to IB timeframe')

    return ib_timeframe


def duration_to_ib(from_dt: datetime, to_dt: datetime) -> str:
    period = to_dt - from_dt
    second_count = int(period.total_seconds())
    day_count = math.floor(second_count / 86400)  # Seconds in day
    year_count = math.floor(day_count / 365)  # Days in year

    if not day_count:
        duration = f'{second_count} S'
    elif not year_count:
        duration = f'{day_count} D'
    else:
        duration = f'{year_count} Y'

    return duration


def timestamp_from_ib(dt: Union[datetime, date]) -> int:
    if type(dt) is date:
        date_time = pytz.utc.localize(datetime.combine(dt, time(0, 0)))
    elif type(dt) is datetime:
        date_time = dt
    else:
        raise ValueError(f'Cannot convert datetime {dt} from IB')

    return int(date_time.timestamp())


def bar_from_ib(ib_bar: BarData, volume_multiplier: int) -> Bar:
    return Bar(
        o=ib_bar.open,
        h=ib_bar.high,
        l=ib_bar.low,
        c=ib_bar.close,
        v=int(ib_bar.volume) * volume_multiplier,
        t=timestamp_from_ib(ib_bar.date),
    )
