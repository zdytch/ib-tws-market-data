from fastapi import APIRouter, HTTPException
from .schemas import IndicatorGet
from . import services

indicator_router = APIRouter(tags=['Indicators'])


@indicator_router.get('/{ticker}', response_model=IndicatorGet)
async def get_indicator(ticker: str, length: int):
    try:
        return await services.get_indicator(ticker, length)
    except:  # TODO: catch business exception
        raise HTTPException(
            status_code=404,
            detail=f'Instrument with ticker {ticker} not found',
        )
