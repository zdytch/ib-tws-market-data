from fastapi import APIRouter, Query
from schemas import Timeframe, BarList, ChartData
import services
from typing import Union


api_router = APIRouter()


@api_router.get('/history', response_model=ChartData)
async def get_historical_data(
    symbol: str, resolution: str, from_: int = Query(..., alias='from'), to: int = ...
):
    if resolution == '1D':
        resolution = 'D'
    bar_list = await services.get_bar_list(symbol, Timeframe(resolution), from_, to)

    return await services.bar_list_to_chart_data(bar_list)


@api_router.get('/symbols')
async def get_info(symbol: str):
    return await services.get_info(symbol)


@api_router.get('/config')
def get_config():
    return services.get_config()
