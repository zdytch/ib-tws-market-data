from bars.models import Timeframe
from datetime import timedelta


def get_step_size(timeframe: Timeframe) -> timedelta:
    if timeframe == Timeframe.M1:
        step_size = timedelta(minutes=1)
    elif timeframe == Timeframe.M5:
        step_size = timedelta(minutes=5)
    elif timeframe == Timeframe.M30:
        step_size = timedelta(minutes=30)
    elif timeframe == Timeframe.M60:
        step_size = timedelta(hours=1)
    elif timeframe == Timeframe.DAY:
        step_size = timedelta(days=1)
    elif timeframe == Timeframe.WEEK:
        step_size = timedelta(days=7)
    elif timeframe == Timeframe.MONTH:
        step_size = timedelta(days=30)  # TODO: Better approach
    else:
        raise ValueError(f'Cannot get step size for timeframe {timeframe}')

    return step_size
