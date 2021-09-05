from fastapi import APIRouter, Query
from schemas import Timeframe, BarData, ChartData
import services
from typing import Union


api_router = APIRouter()


@api_router.get('/historical_data', response_model=Union[BarData, ChartData])
async def get_historical_data(
    ticker: str,
    timeframe: Timeframe,
    from_: int = Query(..., alias='from'),
    to: int = ...,
    chart_format: bool = False,
):
    bar_data = await services.get_bar_data(ticker, timeframe, from_, to)

    if chart_format:
        return await services.bar_data_to_chart_data(bar_data)
    else:
        return bar_data
