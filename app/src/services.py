from schemas import Timeframe, InstrumentType, Exchange, Bar, ChartData
from ib_connector import IBConnector
from datetime import datetime
from config.db import database
import pytz

ibc = IBConnector()


async def get_historical_bars(
    ticker: str, timeframe: Timeframe, from_ts: int, to_ts: int
) -> list[Bar]:
    exchange, symbol = tuple(ticker.split(':'))
    exchange = Exchange(exchange)

    cached_bars = _get_bars_from_cache(symbol, exchange, timeframe, from_ts, to_ts)

    if not cached_bars:
        live_bars = await _get_bars_from_ib(symbol, exchange, timeframe, from_ts, to_ts)
        await _save_bars_to_cache(live_bars)

    return await _get_bars_from_cache(symbol, exchange, timeframe, from_ts, to_ts)


def get_chart_data_from_bars(bar_list: list[Bar]) -> ChartData:
    chart_data = ChartData()

    for bar in bar_list:
        chart_data.o.append(bar.o)
        chart_data.h.append(bar.h)
        chart_data.l.append(bar.l)
        chart_data.c.append(bar.c)
        chart_data.v.append(bar.v)
        chart_data.t.append(bar.t)
    if all(value for value in chart_data.dict().values()):
        chart_data.s = 'ok'

    return chart_data


async def _get_bars_from_cache(
    symbol: str, exchange: Exchange, timeframe: Timeframe, from_ts: int, to_ts
) -> list[Bar]:
    pass


async def _save_bars_to_cache(bars: list[Bar]) -> None:
    pass


async def _get_bars_from_ib(
    symbol: str, exchange: Exchange, timeframe: Timeframe, from_ts: int, to_ts
) -> list[Bar]:
    instrument_type = _get_instrument_type_by_exchange(Exchange(exchange))
    from_dt = datetime.fromtimestamp(from_ts, pytz.utc)
    to_dt = datetime.fromtimestamp(to_ts, pytz.utc)

    return await ibc.get_historical_bars(
        symbol, exchange, instrument_type, timeframe, from_dt, to_dt
    )


def _get_instrument_type_by_exchange(exchange: Exchange) -> InstrumentType:
    if exchange in (Exchange.NASDAQ, Exchange.NYSE):
        instrument_type = InstrumentType.STOCK
    elif exchange in (Exchange.GLOBEX, Exchange.ECBOT, Exchange.NYMEX):
        instrument_type = InstrumentType.FUTURE
    else:
        raise ValueError(f'Cannot get instrument type, exchange unknown: {exchange}')

    return instrument_type
