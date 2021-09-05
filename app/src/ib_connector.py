from ib_insync import IB, Contract, Stock, ContFuture
from schemas import InstrumentType, Bar, Instrument
from datetime import datetime
import ib_utils
from loguru import logger


logger.add(
    'logs/ib_sync_{time}.log',
    format='{time} {level} {message}',
    level='DEBUG',
    rotation='100 MB',
    retention='14 days',
    compression='zip',
)


class IBConnector:
    def __init__(self):
        self._ib = IB()

    @property
    def is_connected(self) -> bool:
        return self._ib.isConnected()

    async def get_historical_bars(
        self,
        instrument: Instrument,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[Bar]:
        await self._connect()

        bars = []
        if self.is_connected:
            contract = await self._get_contract(instrument)
            is_stock = instrument.type == InstrumentType.STOCK
            volume_multiplier = 100 if is_stock else 1

            ib_bars = await self._ib.reqHistoricalDataAsync(
                contract=contract,
                endDateTime=to_dt,
                durationStr=ib_utils.duration_to_ib(from_dt, to_dt),
                barSizeSetting=ib_utils.timeframe_to_ib(instrument.timeframe),
                whatToShow='TRADES',
                useRTH=is_stock,
                formatDate=2,
                keepUpToDate=False,
            )

            for ib_bar in ib_bars:
                bar = ib_utils.bar_from_ib(ib_bar, volume_multiplier)
                bars.append(bar)

        return bars

    async def _connect(self, client_id=1):
        if not self.is_connected:
            try:
                await self._ib.connectAsync('dataserver-ib', 4002, client_id)
            except Exception as error:
                logger.error(error)

    async def _get_contract(self, instrument: Instrument) -> Contract:
        if instrument.type == InstrumentType.STOCK:
            contract = Stock(instrument.symbol, f'SMART:{instrument.exchange}', 'USD')
        elif instrument.type == InstrumentType.FUTURE:
            contract = ContFuture(
                instrument.symbol, f'SMART:{instrument.exchange}', currency='USD'
            )
        else:
            raise ValueError(
                f'Cannot get contract for type {instrument.type}, '
                f'symbol {instrument.symbol}, exchange {instrument.exchange}'
            )

        if contract:
            await self._ib.qualifyContractsAsync(contract)
            if not contract.conId:
                raise ValueError(f'Cannot qualify contract {contract}')

        return contract
