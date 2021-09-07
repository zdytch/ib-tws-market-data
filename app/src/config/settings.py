import os
from loguru import logger


DEBUG = int(os.environ['APP_DEBUG'])

API_URL_PREFIX = '/api/v1'

SECRET_KEY = os.environ['APP_SECRET_KEY']

DB_URL = (
    f'postgresql://{os.getenv("POSTGRES_USER")}:'
    f'{os.getenv("POSTGRES_PASSWORD")}@'
    f'trixter-db:5432/'
    f'{os.getenv("POSTGRES_DB")}'
)

BACKEND_CORS_ORIGINS = [
    'http://localhost:3000',
]

logger.add(
    'logs/mdc_{time}.log',
    format='{time} {level} {message}',
    level='DEBUG',
    rotation='100 MB',
    retention='14 days',
    compression='zip',
)
