from config.db import Session
from instruments import services as instrument_services
from alerts import services as alert_services
from .schemas import BarInfo
from .connector import ibc
from datetime import datetime, timezone, timedelta
from asyncio import Queue, get_event_loop, sleep

_realtime_bar_queue: Queue = Queue()


async def connect_brokers() -> None:
    loop = get_event_loop()
    loop.create_task(_dequeue_realtime_bars())
    loop.create_task(_keep_ib_connected())


async def _connected_callback() -> None:
    pass
    # async with Session() as db:
    #     idea_trades = await trade_services.get_trades_in_idea(db)
    #     idea_instruments = {trade.instrument for trade in idea_trades}

    #     progress_trades = await trade_services.get_trades_in_progress(db)
    #     progress_instruments = {trade.instrument for trade in progress_trades}

    #     for instrument in idea_instruments:
    #         await toggle_realtime_bars(instrument, True)

    #     for instrument in progress_instruments:
    #         await toggle_realtime_ticks(instrument, True)


async def _realtime_bar_callback(bar_info: BarInfo) -> None:
    await _realtime_bar_queue.put(bar_info)


async def _dequeue_realtime_bars() -> None:
    while True:
        bar_info = await _realtime_bar_queue.get()
        await _dequeue_bar(bar_info)

        _realtime_bar_queue.task_done()


async def _dequeue_bar(bar_info: BarInfo) -> None:
    if datetime.now(timezone.utc) - bar_info.timestamp < timedelta(seconds=10):
        async with Session() as db:
            instrument = await instrument_services.get_saved_instrument(
                db, f'{bar_info.exchange}:{bar_info.symbol}'
            )
            await alert_services.check_alerts(instrument, bar_info)


async def _keep_ib_connected() -> None:
    # TODO: Workaround for issue: https://github.com/erdewit/ib_insync/issues/419

    counter = 0
    check_interval = 5
    disconnect_interval = 60

    while True:
        if counter % disconnect_interval == 0:
            ibc.disconnect()

        counter += check_interval

        await ibc.connect()
        await sleep(check_interval)


ibc.subscribe_callbacks(
    connected_callback=_connected_callback,
    realtime_bar_callback=_realtime_bar_callback,
)
