from fastapi import APIRouter, HTTPException

from fastapi_pagination import Page, paginate
from ormar import NoMatch
from .models import InstrumentType
from .schemas import InstrumentGet, InstrumentList, SessionGet
from . import services

instrument_router = APIRouter(tags=['Instruments'])


@instrument_router.get('', response_model=Page[InstrumentList])
async def get_instrument_list(
    search: str = None,
    type: InstrumentType = None,
):
    instruments = await services.get_instrument_list(search, type)

    return paginate(instruments)


@instrument_router.get('/{ticker}', response_model=InstrumentGet)
async def get_instrument(ticker: str):
    try:
        return await services.get_instrument(ticker)
    except NoMatch:
        raise HTTPException(
            status_code=404,
            detail=f'Instrument with ticker {ticker} not found',
        )


@instrument_router.get('/{ticker}/session', response_model=SessionGet)
async def get_session(ticker: str):
    try:
        instrument = await services.get_instrument(ticker)
        return await services.get_session(instrument)
    except NoMatch:
        raise HTTPException(
            status_code=404,
            detail=f'Instrument with ticker {ticker} not found',
        )