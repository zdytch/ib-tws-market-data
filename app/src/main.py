from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import api_router
from config import settings
import debugpy


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix=settings.API_URL_PREFIX)


@app.on_event('startup')
async def startup():
    if settings.DEBUG:
        debugpy.listen(('0.0.0.0', 8888))
