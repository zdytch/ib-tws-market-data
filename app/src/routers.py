from fastapi import APIRouter, Query
from schemas import Bar, Timeframe, Exchange
from ib_connector import IBConnector
from datetime import datetime
import services
import pytz

api_router = APIRouter()

ibc = IBConnector()


@api_router.get('/history', response_model=list[Bar])
async def get_symbol_history(
    ticker: str,
    timeframe: Timeframe,
    from_: int = Query(..., alias='from'),
    to: int = ...,
):
    exchange, symbol = tuple(ticker.split(':'))
    instrument_type = services.get_instrument_type_by_exchange(Exchange(exchange))
    from_dt = datetime.fromtimestamp(from_, pytz.utc)
    to_dt = datetime.fromtimestamp(to, pytz.utc)

    return await ibc.get_historical_bars(
        symbol, exchange, instrument_type, timeframe, from_dt, to_dt
    )
