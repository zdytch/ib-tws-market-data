from fastapi import APIRouter, Query
from schemas import Timeframe, BarList, ChartData
import services
from typing import Union


api_router = APIRouter()


@api_router.get('/historical_data', response_model=Union[BarList, ChartData])
async def get_historical_data(
    ticker: str,
    timeframe: Timeframe,
    from_: int = Query(..., alias='from'),
    to: int = ...,
    chart_format: bool = False,
):
    bar_list = await services.get_bar_list(ticker, timeframe, from_, to)

    if chart_format:
        return await services.bar_list_to_chart_data(bar_list)
    else:
        return bar_list
