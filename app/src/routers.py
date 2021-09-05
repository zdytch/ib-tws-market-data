from fastapi import APIRouter, Query
from schemas import Timeframe, Bar, ChartData, Range
import services
from typing import Union


api_router = APIRouter()


@api_router.get('/historical_data', response_model=Union[list[Bar], ChartData])
async def get_historical_data(
    ticker: str,
    timeframe: Timeframe,
    from_: int = Query(..., alias='from'),
    to: int = ...,
    chart_format: bool = False,
):
    bars = await services.get_historical_bars(
        ticker, timeframe, Range(from_t=from_, to_t=to)
    )

    if chart_format:
        return services.get_chart_data_from_bars(bars)
    else:
        return bars
