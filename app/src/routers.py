from fastapi import APIRouter

api_router = APIRouter()

# @api_router.get('/history')
# async def get_symbol_history(
#     symbol: str, resolution: str, from_: int = Query(..., alias='from'), to: int = ...
# ):
#     if resolution == '1D':
#         resolution = 'D'
#     return await services.get_symbol_history(symbol, resolution, from_, to)
