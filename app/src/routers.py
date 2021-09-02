from fastapi import APIRouter, Query
from schemas import Bar, Timeframe
from ib_connector import IBConnector
from datetime import datetime
import pytz

api_router = APIRouter()

ibc = IBConnector()


@api_router.get('/history', response_model=list[Bar])
async def get_symbol_history(
    symbol: str,
    timeframe: Timeframe,
    from_: int = Query(..., alias='from'),
    to: int = ...,
):
    from_dt = datetime.fromtimestamp(from_, pytz.utc)
    to_dt = datetime.fromtimestamp(to, pytz.utc)

    return await ibc.get_historical_bars(timeframe, from_dt, to_dt)
