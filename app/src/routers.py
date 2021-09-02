from fastapi import APIRouter, Query
from schemas import Timeframe, Exchange, ChartData
from ib_connector import IBConnector
from datetime import datetime
import services
import pytz

api_router = APIRouter()

ibc = IBConnector()


@api_router.get('/history', response_model=ChartData)
async def get_symbol_history(
    ticker: str = Query(..., alias='symbol'),
    timeframe: Timeframe = Query(..., alias='resolution'),
    from_: int = Query(..., alias='from'),
    to: int = ...,
):
    exchange, symbol = tuple(ticker.split(':'))
    instrument_type = services.get_instrument_type_by_exchange(Exchange(exchange))
    from_dt = datetime.fromtimestamp(from_, pytz.utc)
    to_dt = datetime.fromtimestamp(to, pytz.utc)

    bars = await ibc.get_historical_bars(
        symbol, exchange, instrument_type, timeframe, from_dt, to_dt
    )

    return services.convert_bar_list_to_chart_data(bars)


@api_router.get('/symbols')
async def get_symbol_info(symbol: str):
    return await services.get_symbol_info(symbol)


@api_router.get('/config')
def get_config():
    return services.get_config()
