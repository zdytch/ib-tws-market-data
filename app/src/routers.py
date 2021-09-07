from fastapi import APIRouter
from charts.routers import chart_router

api_router = APIRouter()

api_router.include_router(chart_router, prefix='/charts')
