from .schemas import History, Info, Config
from bars.models import Timeframe
from common.schemas import Range
from bars import services as bar_services
from instruments.models import Exchange, InstrumentType
from instruments import services as instrument_services
from loguru import logger


async def get_history(ticker: str, timeframe: str, from_t: int, to_t: int) -> History:
    history = History()
    bars = []
    latest_t = 0

    try:
        instrument = await instrument_services.get_instrument(ticker)
        bar_set = await bar_services.get_bar_set(instrument, Timeframe(timeframe))
        bars = await bar_services.get_bars(bar_set, Range(from_t=from_t, to_t=to_t))
        latest_t = await bar_services.get_latest_timestamp(bar_set)
    except Exception as error:
        logger.error(error)

    for bar in bars:
        history.o.append(bar.o)
        history.h.append(bar.h)
        history.l.append(bar.l)
        history.c.append(bar.c)
        history.v.append(bar.v)
        history.t.append(bar.t)

    if bars:
        history.s = 'ok'
    elif latest_t:
        history.nextTime = latest_t

    return history


async def get_info(ticker: str) -> Info:
    info = Info(name=ticker, ticker=ticker)

    try:
        instrument = await instrument_services.get_instrument(ticker)
        instrument_type = _instrument_type_to_chart(instrument.type)
        timezone, session = _exchange_schedule_to_chart(instrument.exchange)
        price_scale = 10 ** abs(instrument.tick_size.normalize().as_tuple().exponent)
        min_movement = int(instrument.tick_size * price_scale)

        info.type = instrument_type
        info.description = instrument.description
        info.exchange = instrument.exchange
        info.listed_exchange = instrument.exchange
        info.session = session
        info.timezone = timezone
        info.minmov = min_movement
        info.pricescale = price_scale
    except Exception as error:
        logger.error(error)

    return info


def get_config() -> Config:
    return Config(
        supported_resolutions=['1', '5', '30', '1D'],
        supports_search=True,
        supports_group_request=False,
        supports_marks=False,
        supports_timescale_marks=False,
    )


def _instrument_type_to_chart(type: InstrumentType) -> str:
    if type == InstrumentType.STOCK:
        instrument_type = 'stock'
    elif type == InstrumentType.FUTURE:
        instrument_type = 'futures'
    else:
        raise ValueError(f'Cannot convert {type} to InstrumentType')

    return instrument_type


def _exchange_schedule_to_chart(exchange: Exchange) -> tuple[str, str]:
    if exchange in (Exchange.NASDAQ, Exchange.NYSE):
        tz_id = 'America/New_York'
        session = '0930-1600'
    elif exchange == Exchange.NYMEX:
        tz_id = 'America/New_York'
        session = '1800-1700'
    elif exchange == Exchange.GLOBEX:
        tz_id = 'America/Chicago'
        session = '1700-1600'
    elif exchange == Exchange.ECBOT:
        tz_id = 'America/Chicago'
        session = '1900-1320'
    else:
        raise ValueError(f'Cannot get schedule for exchange {exchange}')

    return tz_id, session
