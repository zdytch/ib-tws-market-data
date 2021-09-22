from bars.models import Timeframe


def get_step_size(timeframe: Timeframe):
    if timeframe == Timeframe.M1:
        step_size = 60
    elif timeframe == Timeframe.M5:
        step_size = 60 * 5
    elif timeframe == Timeframe.M30:
        step_size = 60 * 30
    elif timeframe == Timeframe.M60:
        step_size = 60 * 60
    elif timeframe == Timeframe.DAY:
        step_size = 60 * 60 * 24
    elif timeframe == Timeframe.WEEK:
        step_size = 60 * 60 * 24 * 7
    elif timeframe == Timeframe.MONTH:
        step_size = 60 * 60 * 24 * 7 * 4
    else:
        raise ValueError(f'Cannot get step size for timeframe {timeframe}')

    return step_size
