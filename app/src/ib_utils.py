from typing import Union
from ib_insync import BarData
from .schemas import Bar, Timeframe
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
    day_count = math.ceil(period.total_seconds() / 86400)  # Seconds in day
    year_count = math.ceil(day_count / 365)  # Days in year

    # If duration is greater than 365 days, IB TWS requires year instead of day
    if day_count > 365:
        duration = f'{year_count} Y'
    else:
        duration = f'{day_count} D'

    return duration


def timestamp_from_ib(dt: Union[datetime, date]) -> datetime:
    if type(dt) is date:
        date_time = pytz.utc.localize(datetime.combine(dt, time(0, 0)))
    elif type(dt) is datetime:
        date_time = dt
    else:
        raise ValueError(f'Cannot convert datetime {dt} from IB')

    return date_time


def bar_from_ib(ib_bar: BarData, volume_multiplier: int) -> Bar:
    return Bar(
        o=ib_bar.open,
        h=ib_bar.high,
        l=ib_bar.low,
        c=ib_bar.close,
        v=int(ib_bar.volume) * volume_multiplier,
        t=timestamp_from_ib(ib_bar.date),
    )
