from fastapi import APIRouter, Query
from schemas import Bar

api_router = APIRouter()


@api_router.get('/history', response_model=list[Bar])
async def get_symbol_history(
    symbol: str, resolution: str, from_: int = Query(..., alias='from'), to: int = ...
):
    if resolution == '1D':  # TODO: Maybe useless?
        resolution = 'D'

    return await services.get_bars(symbol, resolution, from_, to)
