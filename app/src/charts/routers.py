from fastapi import APIRouter, Query
from .schemas import History, Info, Config
from . import services

chart_router = APIRouter(tags=['Charts'])


@chart_router.get('/history', response_model=History)
async def get_history(
    symbol: str, resolution: str, from_: int = Query(..., alias='from'), to: int = ...
):
    if resolution == '1D':
        resolution = 'D'

    return await services.get_history(symbol, resolution, from_, to)


@chart_router.get('/symbols', response_model=Info)
async def get_info(symbol: str):
    return await services.get_info(symbol)


@chart_router.get('/config', response_model=Config)
def get_config():
    return services.get_config()
