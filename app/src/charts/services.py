from .schemas import History, Info, Config
from bars.models import Bar, Timeframe
from bars import services as bar_services
from instruments.models import Exchange, InstrumentType
from instruments import services as instrument_services


async def get_history(ticker: str, timeframe: str, from_t: int, to_t: int) -> History:
    exchange, symbol = _split_ticker(ticker)
    instrument = await instrument_services.get_instrument(
        symbol=symbol, exchange=exchange
    )
    bars = await bar_services.get_bars(instrument, Timeframe(timeframe), from_t, to_t)

    return await _bar_list_to_history(bars)


async def get_info(ticker: str) -> Info:
    exchange, symbol = _split_ticker(ticker)
    instrument = await instrument_services.get_instrument(
        symbol=symbol, exchange=exchange
    )
    instrument_type = _instrument_type_to_chart(instrument.type)
    timezone, session = _exchange_schedule_to_chart(instrument.exchange)
    price_scale = 10 ** abs(instrument.tick_size.normalize().as_tuple().exponent)
    min_movement = int(instrument.tick_size * price_scale)

    return Info(
        name=ticker,
        ticker=ticker,
        type=instrument_type,
        description=instrument.description,
        exchange=instrument.exchange,
        listed_exchange=instrument.exchange,
        session=session,
        timezone=timezone,
        currency_code='USD',
        has_daily=True,
        has_intraday=True,
        minmov=min_movement,
        pricescale=price_scale,
    )


def get_config() -> Config:
    return Config(
        supported_resolutions=['1', '5', '30', '1D'],
        supports_search=True,
        supports_group_request=False,
        supports_marks=False,
        supports_timescale_marks=False,
    )


def _split_ticker(ticker: str) -> tuple[Exchange, str]:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    return (exchange, symbol)


async def _bar_list_to_history(bars: list[Bar]) -> History:
    history = History()

    for bar in bars:
        history.o.append(bar.o)
        history.h.append(bar.h)
        history.l.append(bar.l)
        history.c.append(bar.c)
        history.v.append(bar.v)
        history.t.append(bar.t)

    if bars:
        history.s = 'ok'
    else:
        pass
        # last_ts = await bar_services.get_last_timestamp(
        #     bar_list.instrument, bar_list.timeframe
        # )
        # history.nextTime = last_ts

    return history


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
