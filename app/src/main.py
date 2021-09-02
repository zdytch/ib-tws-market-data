from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import api_router
from config import settings


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix=settings.API_URL_PREFIX)


# @app.on_event('startup')
# async def startup():
#     db.metadata.create_all(db.engine)  # TODO: Use migrations instead?
#     await db.database.connect()

#     if settings.DEBUG:
#         import debugpy

#         debugpy.listen(('0.0.0.0', 8888))


# @app.on_event('shutdown')
# async def shutdown():
#     await db.database.disconnect()
