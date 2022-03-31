from config.db import DB
from ib.schemas import BarInfo
from . import alert_crud
from indicators import services as indicator_services
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import httpx


async def check_alerts(db: DB, bar_info: BarInfo):
    indicator = await indicator_services.get_indicator(
        db, bar_info.symbol, bar_info.exchange, 5
    )
    alerts = await alert_crud.get_alert_list(
        db, instrument_id=indicator.bar_set.instrument_id
    )

    for alert in alerts:
        await _send_message(alert.external_id)


async def _send_message(message: str):
    url = (
        f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        f'?chat_id={TELEGRAM_CHAT_ID}&text={message}'
    )

    async with httpx.AsyncClient() as client:
        await client.get(url)
