from fastapi import APIRouter
from instruments.routers import instrument_router
from charts.routers import chart_router

api_router = APIRouter()

api_router.include_router(instrument_router, prefix='/instruments')
api_router.include_router(chart_router, prefix='/charts')
