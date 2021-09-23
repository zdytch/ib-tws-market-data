from fastapi import APIRouter
from charts.routers import chart_router
from instruments.routers import instrument_router
from indicators.routers import indicator_router

api_router = APIRouter()

api_router.include_router(chart_router, prefix='/charts')
api_router.include_router(instrument_router, prefix='/instruments')
api_router.include_router(indicator_router, prefix='/indicators')
