from typing import Union
from ib_insync import BarData
from instruments.schemas import Exchange, InstrumentType, TradingSession
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
    total_seconds = int((to_dt - from_dt).total_seconds())
    total_days = math.ceil(total_seconds / 86400)  # Seconds in day
    total_years = math.ceil(total_days / 365)  # Days in year

    if total_seconds < 86400:
        # TWS requires duration to be at least 30 seconds
        total_seconds = total_seconds if total_seconds >= 30 else 30
        duration = f'{total_seconds} S'
    elif total_days < 365:
        duration = f'{total_days} D'
    else:
        duration = f'{total_years} Y'

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


def get_instrument_type_by_exchange(exchange: Exchange) -> InstrumentType:
    if exchange in (Exchange.NASDAQ, Exchange.NYSE):
        instrument_type = InstrumentType.STOCK
    elif exchange in (Exchange.GLOBEX, Exchange.ECBOT, Exchange.NYMEX):
        instrument_type = InstrumentType.FUTURE
    else:
        raise ValueError(f'Cannot get instrument type, exchange unknown: {exchange}')

    return instrument_type


def get_nearest_trading_session(trading_hours: str, tz_id: str) -> TradingSession:
    session = None
    session_tz = pytz.timezone(tz_id)
    for ib_session in trading_hours.split(';'):
        if not 'CLOSED' in ib_session:
            ib_open, ib_close = tuple(ib_session.split('-'))
            open = session_tz.localize(datetime.strptime(ib_open, '%Y%m%d:%H%M'))
            close = session_tz.localize(datetime.strptime(ib_close, '%Y%m%d:%H%M'))
            session = TradingSession(
                open_t=int(open.timestamp()), close_t=int(close.timestamp())
            )
            break

    if not session:
        raise ValueError(
            f'Cannot get nearest trading session from trading hours {trading_hours}'
        )

    return session
