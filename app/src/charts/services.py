from .schemas import ChartData
from decimal import Decimal
from bars.schemas import BarList, Timeframe
from bars import services as bar_services
from instruments.schemas import Exchange, InstrumentType
from instruments import services as instrument_services
from .. import cache


async def get_history(ticker: str, timeframe: str, from_t: int, to_t: int) -> ChartData:
    instrument = await instrument_services.get_instrument(ticker)
    bar_list = await bar_services.get_bar_list(
        instrument, Timeframe(timeframe), from_t, to_t
    )

    return await _bar_list_to_chart_data(bar_list)


async def get_info(ticker: str) -> dict:
    instrument = await instrument_services.get_instrument(ticker)
    instrument_type = _instrument_type_to_chart(instrument.type)
    timezone, session = _exchange_schedule_to_chart(instrument.exchange)
    price_scale = 10 ** abs(
        Decimal(str(instrument.tick_size)).normalize().as_tuple().exponent
    )
    min_movement = int(instrument.tick_size * price_scale)

    return {
        'name': ticker,
        'ticker': ticker,
        'type': instrument_type,
        'description': instrument.description,
        'exchange': instrument.exchange,
        'listed_exchange': instrument.exchange,
        'session': session,
        'timezone': timezone,
        'currency_code': 'USD',
        'has_daily': True,
        'has_intraday': True,
        'minmov': min_movement,
        'pricescale': price_scale,
    }


def get_config() -> dict:
    return {
        'supported_resolutions': ['1', '5', '30', '1D'],
        'supports_search': True,
        'supports_group_request': False,
        'supports_marks': False,
        'supports_timescale_marks': False,
    }


async def _bar_list_to_chart_data(data: BarList) -> ChartData:
    chart_data = ChartData()

    for bar in data.bars:
        chart_data.o.append(bar.o)
        chart_data.h.append(bar.h)
        chart_data.l.append(bar.l)
        chart_data.c.append(bar.c)
        chart_data.v.append(bar.v)
        chart_data.t.append(bar.t)

    if data.bars:
        chart_data.s = 'ok'
    else:
        last_ts = await cache.get_last_timestamp(data.instrument, data.timeframe)
        chart_data.next_time = last_ts

    return chart_data


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
