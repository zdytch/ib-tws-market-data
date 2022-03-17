from fastapi import APIRouter, HTTPException, Depends
from config.db import DB, get_db
from fastapi_pagination import Page, paginate
from .models import InstrumentType
from .schemas import InstrumentGet, InstrumentList, SessionGet
from . import services

instrument_router = APIRouter(tags=['Instruments'])


@instrument_router.get('', response_model=Page[InstrumentList])
async def get_instrument_list(
    search: str | None = None,
    type: InstrumentType | None = None,
    db: DB = Depends(get_db),
):
    instruments = await services.filter_instruments(db, search, type)

    return paginate(instruments)


@instrument_router.get('/{ticker}', response_model=InstrumentGet)
async def get_instrument(ticker: str, db: DB = Depends(get_db)):
    try:
        return await services.get_saved_instrument(db, ticker)
    except:  # TODO: catch business exception
        raise HTTPException(
            status_code=404,
            detail=f'Instrument with ticker {ticker} not found',
        )


@instrument_router.get('/{ticker}/session', response_model=SessionGet)
async def get_trading_session(ticker: str, db: DB = Depends(get_db)):
    try:
        instrument = await services.get_saved_instrument(db, ticker)

        return await services.get_nearest_trading_session(db, instrument)

    except:  # TODO: catch business exception
        raise HTTPException(
            status_code=404,
            detail=f'Instrument with ticker {ticker} not found',
        )
